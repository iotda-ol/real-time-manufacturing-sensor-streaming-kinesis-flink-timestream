package com.manufacturing.analytics;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.connector.kinesis.source.KinesisStreamsSource;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

/**
 * Manufacturing Sensor Stream Processor
 * Processes sensor data from Kinesis and writes aggregated metrics to Timestream
 */
public class SensorStreamProcessor {
    
    private static final Logger LOG = LoggerFactory.getLogger(SensorStreamProcessor.class);
    
    public static void main(String[] args) throws Exception {
        
        // Set up streaming execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Enable checkpointing for fault tolerance
        env.enableCheckpointing(60000); // checkpoint every 60 seconds
        
        // Parse application properties
        final ParameterTool params = ParameterTool.fromArgs(args);
        final String region = params.get("aws.region", "us-east-1");
        final String streamName = params.get("kinesis.stream.name");
        final String timestreamDatabase = params.get("timestream.database");
        final String timestreamTable = params.get("timestream.table");
        final String streamArn = params.get("kinesis.stream.arn");
        
        LOG.info("Starting Sensor Stream Processor");
        LOG.info("Kinesis Stream: {}", streamName);
        LOG.info("Timestream Database: {}", timestreamDatabase);
        LOG.info("Timestream Table: {}", timestreamTable);
        
        // Configure Kinesis Source
        Properties consumerConfig = new Properties();
        consumerConfig.setProperty("aws.region", region);
        consumerConfig.setProperty("flink.stream.initpos", "LATEST");
        
        // Use stream ARN passed from configuration
        KinesisStreamsSource<String> kinesisSource = KinesisStreamsSource.<String>builder()
                .setStreamArn(streamArn)
                .setDeserializationSchema(new SimpleStringSchema())
                .build();
        
        // Read from Kinesis
        DataStream<String> kinesisStream = env.fromSource(
                kinesisSource,
                WatermarkStrategy.<String>forBoundedOutOfOrderness(Duration.ofSeconds(10))
                        .withTimestampAssigner((event, timestamp) -> System.currentTimeMillis()),
                "Kinesis Source"
        );
        
        // Parse JSON and create SensorReading objects
        DataStream<SensorReading> sensorReadings = kinesisStream
                .map(new JsonToSensorReading())
                .name("Parse JSON");
        
        // Aggregate metrics by machine and sensor type over 1-minute windows
        DataStream<AggregatedMetrics> aggregatedMetrics = sensorReadings
                .keyBy(reading -> reading.machineId + "-" + reading.sensorType)
                .window(TumblingEventTimeWindows.of(Time.minutes(1)))
                .process(new AggregationFunction())
                .name("Aggregate Metrics");
        
        // Write to Timestream
        aggregatedMetrics.addSink(new TimestreamSink(region, timestreamDatabase, timestreamTable))
                .name("Timestream Sink");
        
        // Execute the Flink job
        env.execute("Manufacturing Sensor Stream Processor");
    }
    
    /**
     * Sensor Reading data class
     */
    public static class SensorReading {
        public String machineId;
        public String sensorType;
        public double value;
        public String unit;
        public String status;
        public long timestamp;
        public String location;
        public String productionLine;
        
        public SensorReading() {}
        
        public SensorReading(String machineId, String sensorType, double value, 
                           String unit, String status, long timestamp,
                           String location, String productionLine) {
            this.machineId = machineId;
            this.sensorType = sensorType;
            this.value = value;
            this.unit = unit;
            this.status = status;
            this.timestamp = timestamp;
            this.location = location;
            this.productionLine = productionLine;
        }
    }
    
    /**
     * Aggregated Metrics data class
     */
    public static class AggregatedMetrics {
        public String machineId;
        public String sensorType;
        public double avgValue;
        public double minValue;
        public double maxValue;
        public long count;
        public long anomalyCount;
        public long windowStart;
        public long windowEnd;
        public String location;
        public String productionLine;
        
        public AggregatedMetrics() {}
    }
    
    /**
     * Map function to parse JSON to SensorReading
     */
    public static class JsonToSensorReading implements MapFunction<String, SensorReading> {
        
        private final Gson gson = new Gson();
        
        @Override
        public SensorReading map(String json) throws Exception {
            try {
                JsonObject jsonObject = gson.fromJson(json, JsonObject.class);
                JsonObject metadata = jsonObject.getAsJsonObject("metadata");
                
                SensorReading reading = new SensorReading();
                reading.machineId = jsonObject.get("machine_id").getAsString();
                reading.sensorType = jsonObject.get("sensor_type").getAsString();
                reading.value = jsonObject.get("value").getAsDouble();
                reading.unit = jsonObject.get("unit").getAsString();
                reading.status = jsonObject.get("status").getAsString();
                reading.timestamp = System.currentTimeMillis();
                reading.location = metadata.get("location").getAsString();
                reading.productionLine = metadata.get("production_line").getAsString();
                
                return reading;
                
            } catch (Exception e) {
                LOG.error("Error parsing JSON: {}", json, e);
                throw e;
            }
        }
    }
    
    /**
     * Process window function to aggregate sensor readings
     */
    public static class AggregationFunction 
            extends ProcessWindowFunction<SensorReading, AggregatedMetrics, String, TimeWindow> {
        
        @Override
        public void process(String key, Context context, 
                          Iterable<SensorReading> readings, 
                          Collector<AggregatedMetrics> out) {
            
            double sum = 0;
            double min = Double.MAX_VALUE;
            double max = Double.MIN_VALUE;
            long count = 0;
            long anomalyCount = 0;
            
            String machineId = null;
            String sensorType = null;
            String location = null;
            String productionLine = null;
            
            for (SensorReading reading : readings) {
                sum += reading.value;
                min = Math.min(min, reading.value);
                max = Math.max(max, reading.value);
                count++;
                
                if ("ANOMALY".equals(reading.status)) {
                    anomalyCount++;
                }
                
                if (machineId == null) {
                    machineId = reading.machineId;
                    sensorType = reading.sensorType;
                    location = reading.location;
                    productionLine = reading.productionLine;
                }
            }
            
            if (count > 0) {
                AggregatedMetrics metrics = new AggregatedMetrics();
                metrics.machineId = machineId;
                metrics.sensorType = sensorType;
                metrics.avgValue = sum / count;
                metrics.minValue = min;
                metrics.maxValue = max;
                metrics.count = count;
                metrics.anomalyCount = anomalyCount;
                metrics.windowStart = context.window().getStart();
                metrics.windowEnd = context.window().getEnd();
                metrics.location = location;
                metrics.productionLine = productionLine;
                
                out.collect(metrics);
            }
        }
    }
}
