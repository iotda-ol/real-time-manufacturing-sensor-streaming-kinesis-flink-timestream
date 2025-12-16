package com.manufacturing.analytics;

import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.timestreamwrite.TimestreamWriteClient;
import software.amazon.awssdk.services.timestreamwrite.model.Dimension;
import software.amazon.awssdk.services.timestreamwrite.model.MeasureValueType;
import software.amazon.awssdk.services.timestreamwrite.model.RejectedRecord;
import software.amazon.awssdk.services.timestreamwrite.model.RejectedRecordsException;
import software.amazon.awssdk.services.timestreamwrite.model.TimeUnit;
import software.amazon.awssdk.services.timestreamwrite.model.WriteRecordsRequest;
import software.amazon.awssdk.services.timestreamwrite.model.WriteRecordsResponse;

import java.util.ArrayList;
import java.util.List;

/**
 * Custom Flink Sink to write data to Amazon Timestream
 */
public class TimestreamSink extends RichSinkFunction<SensorStreamProcessor.AggregatedMetrics> {
    
    private static final Logger LOG = LoggerFactory.getLogger(TimestreamSink.class);
    
    private final String region;
    private final String databaseName;
    private final String tableName;
    
    private transient TimestreamWriteClient timestreamClient;
    
    public TimestreamSink(String region, String databaseName, String tableName) {
        this.region = region;
        this.databaseName = databaseName;
        this.tableName = tableName;
    }
    
    @Override
    public void open(Configuration parameters) throws Exception {
        super.open(parameters);
        
        // Initialize Timestream client
        timestreamClient = TimestreamWriteClient.builder()
                .region(Region.of(region))
                .build();
        
        LOG.info("Timestream client initialized for region: {}", region);
    }
    
    @Override
    public void invoke(SensorStreamProcessor.AggregatedMetrics metrics, Context context) throws Exception {
        try {
            List<software.amazon.awssdk.services.timestreamwrite.model.Record> records = createTimestreamRecords(metrics);
            
            WriteRecordsRequest writeRecordsRequest = WriteRecordsRequest.builder()
                    .databaseName(databaseName)
                    .tableName(tableName)
                    .records(records)
                    .build();
            
            WriteRecordsResponse response = timestreamClient.writeRecords(writeRecordsRequest);
            
            LOG.debug("Written {} records to Timestream for machine: {}, sensor: {}", 
                     records.size(), metrics.machineId, metrics.sensorType);
            
        } catch (RejectedRecordsException e) {
            LOG.error("Rejected records exception: {}", e.getMessage());
            for (RejectedRecord rejectedRecord : e.rejectedRecords()) {
                LOG.error("Rejected record: {}", rejectedRecord.reason());
            }
            throw e;
            
        } catch (Exception e) {
            LOG.error("Error writing to Timestream", e);
            throw e;
        }
    }
    
    /**
     * Create Timestream records from aggregated metrics
     */
    private List<software.amazon.awssdk.services.timestreamwrite.model.Record> createTimestreamRecords(SensorStreamProcessor.AggregatedMetrics metrics) {
        List<software.amazon.awssdk.services.timestreamwrite.model.Record> records = new ArrayList<>();
        
        String currentTime = String.valueOf(System.currentTimeMillis());
        
        // Common dimensions for all records
        List<Dimension> dimensions = new ArrayList<>();
        dimensions.add(Dimension.builder().name("machine_id").value(metrics.machineId).build());
        dimensions.add(Dimension.builder().name("sensor_type").value(metrics.sensorType).build());
        dimensions.add(Dimension.builder().name("location").value(metrics.location).build());
        dimensions.add(Dimension.builder().name("production_line").value(metrics.productionLine).build());
        
        // Average value record
        records.add(software.amazon.awssdk.services.timestreamwrite.model.Record.builder()
                .dimensions(dimensions)
                .measureName("avg_value")
                .measureValue(String.valueOf(metrics.avgValue))
                .measureValueType(MeasureValueType.DOUBLE)
                .time(currentTime)
                .timeUnit(TimeUnit.MILLISECONDS)
                .build());
        
        // Min value record
        records.add(software.amazon.awssdk.services.timestreamwrite.model.Record.builder()
                .dimensions(dimensions)
                .measureName("min_value")
                .measureValue(String.valueOf(metrics.minValue))
                .measureValueType(MeasureValueType.DOUBLE)
                .time(currentTime)
                .timeUnit(TimeUnit.MILLISECONDS)
                .build());
        
        // Max value record
        records.add(software.amazon.awssdk.services.timestreamwrite.model.Record.builder()
                .dimensions(dimensions)
                .measureName("max_value")
                .measureValue(String.valueOf(metrics.maxValue))
                .measureValueType(MeasureValueType.DOUBLE)
                .time(currentTime)
                .timeUnit(TimeUnit.MILLISECONDS)
                .build());
        
        // Count record
        records.add(software.amazon.awssdk.services.timestreamwrite.model.Record.builder()
                .dimensions(dimensions)
                .measureName("record_count")
                .measureValue(String.valueOf(metrics.count))
                .measureValueType(MeasureValueType.BIGINT)
                .time(currentTime)
                .timeUnit(TimeUnit.MILLISECONDS)
                .build());
        
        // Anomaly count record
        records.add(software.amazon.awssdk.services.timestreamwrite.model.Record.builder()
                .dimensions(dimensions)
                .measureName("anomaly_count")
                .measureValue(String.valueOf(metrics.anomalyCount))
                .measureValueType(MeasureValueType.BIGINT)
                .time(currentTime)
                .timeUnit(TimeUnit.MILLISECONDS)
                .build());
        
        return records;
    }
    
    @Override
    public void close() throws Exception {
        super.close();
        if (timestreamClient != null) {
            timestreamClient.close();
            LOG.info("Timestream client closed");
        }
    }
}
