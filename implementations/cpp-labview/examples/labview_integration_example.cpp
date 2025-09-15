/**
 * LabVIEW Direct Variant/Cluster Integration Example
 * Demonstrates direct conversion from LabVIEW data to CFG++ files
 */

#include "../cfgpp_parser.h"
#include <iostream>
#include <vector>
#include <cstring>

// Simulate LabVIEW data structures for demonstration
struct MockLabViewVariant {
    LabViewDataHeader header;
    uint8_t data[256];
};

struct MockLabViewCluster {
    LabViewDataHeader header;
    uint8_t data[1024];
};

// Helper function to create a mock LabVIEW string variant
MockLabViewVariant create_string_variant(const std::string& str) {
    MockLabViewVariant variant = {};
    variant.header.type_code = LABVIEW_TYPE_STRING;
    variant.header.flags = 0;
    variant.header.data_size = 4 + str.length(); // 4 bytes for length prefix
    variant.header.dimensions = 0;
    
    // Write string length (LabVIEW format)
    *reinterpret_cast<uint32_t*>(variant.data) = str.length();
    // Write string data
    memcpy(variant.data + 4, str.c_str(), str.length());
    
    return variant;
}

// Helper function to create a mock LabVIEW double variant
MockLabViewVariant create_double_variant(double value) {
    MockLabViewVariant variant = {};
    variant.header.type_code = LABVIEW_TYPE_DBL;
    variant.header.flags = 0;
    variant.header.data_size = sizeof(double);
    variant.header.dimensions = 0;
    
    *reinterpret_cast<double*>(variant.data) = value;
    
    return variant;
}

// Helper function to create a mock LabVIEW integer variant
MockLabViewVariant create_integer_variant(int32_t value) {
    MockLabViewVariant variant = {};
    variant.header.type_code = LABVIEW_TYPE_I32;
    variant.header.flags = 0;
    variant.header.data_size = sizeof(int32_t);
    variant.header.dimensions = 0;
    
    *reinterpret_cast<int32_t*>(variant.data) = value;
    
    return variant;
}

// Helper function to create a mock LabVIEW boolean variant
MockLabViewVariant create_boolean_variant(bool value) {
    MockLabViewVariant variant = {};
    variant.header.type_code = LABVIEW_TYPE_BOOLEAN;
    variant.header.flags = 0;
    variant.header.data_size = sizeof(uint8_t);
    variant.header.dimensions = 0;
    
    variant.data[0] = value ? 1 : 0;
    
    return variant;
}

// Helper function to create a mock LabVIEW cluster
MockLabViewCluster create_measurement_cluster() {
    MockLabViewCluster cluster = {};
    cluster.header.type_code = LABVIEW_TYPE_CLUSTER;
    cluster.header.flags = 0;
    cluster.header.dimensions = 0;
    
    size_t offset = 0;
    
    // Field 1: Sample Rate (I32)
    LabViewDataHeader* field1_header = reinterpret_cast<LabViewDataHeader*>(cluster.data + offset);
    field1_header->type_code = LABVIEW_TYPE_I32;
    field1_header->data_size = sizeof(int32_t);
    offset += sizeof(LabViewDataHeader);
    *reinterpret_cast<int32_t*>(cluster.data + offset) = 1000;
    offset += sizeof(int32_t);
    
    // Field 2: Voltage Threshold (DBL)
    LabViewDataHeader* field2_header = reinterpret_cast<LabViewDataHeader*>(cluster.data + offset);
    field2_header->type_code = LABVIEW_TYPE_DBL;
    field2_header->data_size = sizeof(double);
    offset += sizeof(LabViewDataHeader);
    *reinterpret_cast<double*>(cluster.data + offset) = 3.14159;
    offset += sizeof(double);
    
    // Field 3: Enable Logging (BOOLEAN)
    LabViewDataHeader* field3_header = reinterpret_cast<LabViewDataHeader*>(cluster.data + offset);
    field3_header->type_code = LABVIEW_TYPE_BOOLEAN;
    field3_header->data_size = sizeof(uint8_t);
    offset += sizeof(LabViewDataHeader);
    cluster.data[offset] = 1; // true
    offset += sizeof(uint8_t);
    
    // Field 4: Device Name (STRING)
    LabViewDataHeader* field4_header = reinterpret_cast<LabViewDataHeader*>(cluster.data + offset);
    field4_header->type_code = LABVIEW_TYPE_STRING;
    std::string device_name = "NI-DAQmx Device";
    field4_header->data_size = 4 + device_name.length();
    offset += sizeof(LabViewDataHeader);
    *reinterpret_cast<uint32_t*>(cluster.data + offset) = device_name.length();
    offset += 4;
    memcpy(cluster.data + offset, device_name.c_str(), device_name.length());
    offset += device_name.length();
    
    cluster.header.data_size = offset;
    return cluster;
}

int main() {
    std::cout << "CFG++ LabVIEW Direct Integration Example" << std::endl;
    std::cout << "========================================" << std::endl << std::endl;
    
    // Example 1: Direct variant to CFG++ file
    std::cout << "Example 1: Convert LabVIEW String Variant to CFG++ File" << std::endl;
    std::cout << "-------------------------------------------------------" << std::endl;
    
    auto string_variant = create_string_variant("Hello from LabVIEW!");
    size_t variant_size = sizeof(LabViewDataHeader) + string_variant.header.data_size;
    
    CfgppResult result = cfgpp_variant_to_file(&string_variant, variant_size, "string_output.cfgpp");
    if (result == CFGPP_SUCCESS) {
        std::cout << "✓ Successfully wrote string variant to string_output.cfgpp" << std::endl;
    } else {
        std::cout << "✗ Failed to write string variant: " << result << std::endl;
    }
    
    // Example 2: Convert double variant to string
    std::cout << std::endl << "Example 2: Convert LabVIEW Double Variant to CFG++ String" << std::endl;
    std::cout << "-----------------------------------------------------------" << std::endl;
    
    auto double_variant = create_double_variant(42.123456);
    variant_size = sizeof(LabViewDataHeader) + double_variant.header.data_size;
    
    char output_buffer[256];
    size_t actual_size;
    result = cfgpp_variant_to_string(&double_variant, variant_size, output_buffer, sizeof(output_buffer), &actual_size);
    if (result == CFGPP_SUCCESS) {
        std::cout << "✓ CFG++ representation: " << std::string(output_buffer, actual_size) << std::endl;
    } else {
        std::cout << "✗ Failed to convert double variant: " << result << std::endl;
    }
    
    // Example 3: Convert cluster to CFG++ file
    std::cout << std::endl << "Example 3: Convert LabVIEW Measurement Cluster to CFG++ File" << std::endl;
    std::cout << "-------------------------------------------------------------" << std::endl;
    
    auto measurement_cluster = create_measurement_cluster();
    size_t cluster_size = sizeof(LabViewDataHeader) + measurement_cluster.header.data_size;
    
    // Define field names for the cluster
    const char* field_names[] = {
        "sample_rate",
        "voltage_threshold", 
        "enable_logging",
        "device_name"
    };
    size_t field_count = sizeof(field_names) / sizeof(field_names[0]);
    
    result = cfgpp_cluster_to_file(&measurement_cluster, cluster_size, field_names, field_count, 
                                   "measurement_config.cfgpp");
    if (result == CFGPP_SUCCESS) {
        std::cout << "✓ Successfully wrote measurement cluster to measurement_config.cfgpp" << std::endl;
        std::cout << "  Fields: sample_rate, voltage_threshold, enable_logging, device_name" << std::endl;
    } else {
        std::cout << "✗ Failed to write measurement cluster: " << result << std::endl;
    }
    
    // Example 4: Multiple variant types demonstration
    std::cout << std::endl << "Example 4: Multiple Data Types" << std::endl;
    std::cout << "------------------------------" << std::endl;
    
    struct {
        const char* name;
        MockLabViewVariant variant;
        const char* filename;
    } test_cases[] = {
        {"Integer (1000)", create_integer_variant(1000), "integer_test.cfgpp"},
        {"Boolean (true)", create_boolean_variant(true), "boolean_test.cfgpp"},
        {"Double (π)", create_double_variant(3.14159265359), "pi_test.cfgpp"},
        {"String (Config)", create_string_variant("Configuration Data"), "config_test.cfgpp"}
    };
    
    for (auto& test_case : test_cases) {
        size_t size = sizeof(LabViewDataHeader) + test_case.variant.header.data_size;
        result = cfgpp_variant_to_file(&test_case.variant, size, test_case.filename);
        
        if (result == CFGPP_SUCCESS) {
            std::cout << "✓ " << test_case.name << " → " << test_case.filename << std::endl;
        } else {
            std::cout << "✗ " << test_case.name << " failed (" << result << ")" << std::endl;
        }
    }
    
    // Performance demonstration
    std::cout << std::endl << "Performance Test: 1000 Variant Conversions" << std::endl;
    std::cout << "===========================================";
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    int success_count = 0;
    for (int i = 0; i < 1000; i++) {
        auto test_variant = create_double_variant(i * 0.001);
        size_t size = sizeof(LabViewDataHeader) + test_variant.header.data_size;
        
        char buffer[128];
        size_t buffer_size;
        result = cfgpp_variant_to_string(&test_variant, size, buffer, sizeof(buffer), &buffer_size);
        if (result == CFGPP_SUCCESS) {
            success_count++;
        }
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
    
    std::cout << std::endl;
    std::cout << "Results: " << success_count << "/1000 conversions successful" << std::endl;
    std::cout << "Time: " << duration.count() << " microseconds" << std::endl;
    std::cout << "Average: " << (duration.count() / 1000.0) << " µs per conversion" << std::endl;
    std::cout << "Throughput: " << (1000000000.0 / duration.count()) << " conversions/second" << std::endl;
    
    std::cout << std::endl << "LabVIEW Integration Example Complete!" << std::endl;
    std::cout << "Check the generated .cfgpp files for results." << std::endl;
    
    return 0;
}
