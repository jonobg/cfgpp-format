/**
 * LabVIEW Integration Example for CFG++ Parser DLL
 * Demonstrates high-performance parsing and data access patterns
 */

#include "../cfgpp_parser.h"
#include <iostream>
#include <chrono>
#include <string>

// Example CFG++ configuration
const char* EXAMPLE_CONFIG = R"(
// Example configuration for LabVIEW integration
measurement_config {
    sample_rate = 1000;
    channels = ["voltage", "current", "temperature"];
    trigger_threshold = 2.5;
    enable_logging = true;
    output_format = "binary";
    
    calibration {
        voltage_offset = 0.01;
        current_gain = 1.02;
        temp_coefficients = [0.001, -0.0001, 0.000001];
    }
}

// Enumerated instrument types
enum InstrumentType {
    MULTIMETER;
    OSCILLOSCOPE;
    FUNCTION_GENERATOR;
    POWER_SUPPLY;
}

// Instrument definitions
instruments {
    primary = {
        type = MULTIMETER;
        address = "USB0::0x1234::0x5678::INSTR";
        timeout = 5000;
    };
    
    secondary = {
        type = OSCILLOSCOPE;
        address = "TCPIP::192.168.1.100::INSTR";
        timeout = 10000;
    };
}
)";

void print_value_info(CfgppValueHandle value, const std::string& name, int indent = 0) {
    std::string prefix(indent * 2, ' ');
    
    CfgppValueType type;
    if (cfgpp_value_get_type(value, &type) != CFGPP_SUCCESS) {
        std::cout << prefix << name << ": <error getting type>" << std::endl;
        return;
    }
    
    switch (type) {
        case CFGPP_TYPE_STRING: {
            char buffer[256];
            size_t actual_length;
            if (cfgpp_value_get_string(value, buffer, sizeof(buffer), &actual_length) == CFGPP_SUCCESS) {
                std::cout << prefix << name << ": \"" << buffer << "\" (string)" << std::endl;
            }
            break;
        }
        
        case CFGPP_TYPE_INTEGER: {
            int64_t val;
            if (cfgpp_value_get_integer(value, &val) == CFGPP_SUCCESS) {
                std::cout << prefix << name << ": " << val << " (integer)" << std::endl;
            }
            break;
        }
        
        case CFGPP_TYPE_DOUBLE: {
            double val;
            if (cfgpp_value_get_double(value, &val) == CFGPP_SUCCESS) {
                std::cout << prefix << name << ": " << val << " (double)" << std::endl;
            }
            break;
        }
        
        case CFGPP_TYPE_BOOLEAN: {
            int val;
            if (cfgpp_value_get_boolean(value, &val) == CFGPP_SUCCESS) {
                std::cout << prefix << name << ": " << (val ? "true" : "false") << " (boolean)" << std::endl;
            }
            break;
        }
        
        case CFGPP_TYPE_OBJECT: {
            std::cout << prefix << name << ": {object}" << std::endl;
            size_t size;
            if (cfgpp_value_get_object_size(value, &size) == CFGPP_SUCCESS) {
                for (size_t i = 0; i < size; i++) {
                    char key_buffer[128];
                    size_t key_length;
                    CfgppValueHandle child_value;
                    
                    if (cfgpp_value_get_object_key_at(value, i, key_buffer, sizeof(key_buffer), &key_length) == CFGPP_SUCCESS &&
                        cfgpp_value_get_object_value_at(value, i, &child_value) == CFGPP_SUCCESS) {
                        print_value_info(child_value, key_buffer, indent + 1);
                    }
                }
            }
            break;
        }
        
        case CFGPP_TYPE_ARRAY: {
            size_t size;
            if (cfgpp_value_get_array_size(value, &size) == CFGPP_SUCCESS) {
                std::cout << prefix << name << ": [array of " << size << " elements]" << std::endl;
                for (size_t i = 0; i < size; i++) {
                    CfgppValueHandle element;
                    if (cfgpp_value_get_array_element(value, i, &element) == CFGPP_SUCCESS) {
                        print_value_info(element, "[" + std::to_string(i) + "]", indent + 1);
                    }
                }
            }
            break;
        }
        
        case CFGPP_TYPE_ENUM: {
            char buffer[128];
            size_t actual_length;
            if (cfgpp_value_get_string(value, buffer, sizeof(buffer), &actual_length) == CFGPP_SUCCESS) {
                std::cout << prefix << name << ": " << buffer << " (enum)" << std::endl;
            }
            break;
        }
        
        default:
            std::cout << prefix << name << ": <unknown type>" << std::endl;
            break;
    }
}

int main() {
    std::cout << "CFG++ Parser DLL - LabVIEW Integration Example" << std::endl;
    std::cout << "================================================" << std::endl;
    
    // Create parser instance
    CfgppParserHandle parser;
    CfgppResult result = cfgpp_parser_create(&parser);
    if (result != CFGPP_SUCCESS) {
        std::cout << "Failed to create parser: " << result << std::endl;
        return 1;
    }
    
    // Performance measurement
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Parse the configuration
    CfgppValueHandle config_root;
    result = cfgpp_parse_string(parser, EXAMPLE_CONFIG, strlen(EXAMPLE_CONFIG), &config_root);
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
    
    if (result != CFGPP_SUCCESS) {
        std::cout << "Failed to parse configuration: " << result << std::endl;
        
        // Get error details
        char error_buffer[512];
        size_t error_length;
        int error_line, error_column;
        
        if (cfgpp_get_last_error_message(parser, error_buffer, sizeof(error_buffer), &error_length) == CFGPP_SUCCESS) {
            std::cout << "Error: " << error_buffer << std::endl;
        }
        
        if (cfgpp_get_last_error_location(parser, &error_line, &error_column) == CFGPP_SUCCESS) {
            std::cout << "Location: line " << error_line << ", column " << error_column << std::endl;
        }
        
        cfgpp_parser_destroy(parser);
        return 1;
    }
    
    std::cout << "Parsing completed in " << duration.count() << " microseconds" << std::endl;
    std::cout << std::endl;
    
    // Display parsed configuration
    std::cout << "Parsed Configuration Structure:" << std::endl;
    std::cout << "==============================" << std::endl;
    print_value_info(config_root, "root");
    
    std::cout << std::endl;
    
    // Demonstrate specific value access (typical LabVIEW pattern)
    std::cout << "Accessing Specific Values (LabVIEW Style):" << std::endl;
    std::cout << "==========================================" << std::endl;
    
    // Access nested measurement config
    CfgppValueHandle measurement_config;
    if (cfgpp_value_get_object_value_by_key(config_root, "measurement_config", &measurement_config) == CFGPP_SUCCESS) {
        // Get sample rate
        CfgppValueHandle sample_rate_value;
        if (cfgpp_value_get_object_value_by_key(measurement_config, "sample_rate", &sample_rate_value) == CFGPP_SUCCESS) {
            int64_t sample_rate;
            if (cfgpp_value_get_integer(sample_rate_value, &sample_rate) == CFGPP_SUCCESS) {
                std::cout << "Sample Rate: " << sample_rate << " Hz" << std::endl;
            }
        }
        
        // Get trigger threshold
        CfgppValueHandle threshold_value;
        if (cfgpp_value_get_object_value_by_key(measurement_config, "trigger_threshold", &threshold_value) == CFGPP_SUCCESS) {
            double threshold;
            if (cfgpp_value_get_double(threshold_value, &threshold) == CFGPP_SUCCESS) {
                std::cout << "Trigger Threshold: " << threshold << " V" << std::endl;
            }
        }
        
        // Get channels array
        CfgppValueHandle channels_value;
        if (cfgpp_value_get_object_value_by_key(measurement_config, "channels", &channels_value) == CFGPP_SUCCESS) {
            size_t channel_count;
            if (cfgpp_value_get_array_size(channels_value, &channel_count) == CFGPP_SUCCESS) {
                std::cout << "Channels (" << channel_count << " total): ";
                for (size_t i = 0; i < channel_count; i++) {
                    CfgppValueHandle channel;
                    if (cfgpp_value_get_array_element(channels_value, i, &channel) == CFGPP_SUCCESS) {
                        char channel_name[64];
                        size_t name_length;
                        if (cfgpp_value_get_string(channel, channel_name, sizeof(channel_name), &name_length) == CFGPP_SUCCESS) {
                            std::cout << channel_name;
                            if (i < channel_count - 1) std::cout << ", ";
                        }
                    }
                }
                std::cout << std::endl;
            }
        }
    }
    
    // Performance benchmark
    std::cout << std::endl;
    std::cout << "Performance Benchmark:" << std::endl;
    std::cout << "=====================" << std::endl;
    
    const int ITERATIONS = 1000;
    auto bench_start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < ITERATIONS; i++) {
        CfgppValueHandle temp_config;
        cfgpp_parse_string(parser, EXAMPLE_CONFIG, strlen(EXAMPLE_CONFIG), &temp_config);
        cfgpp_value_destroy(temp_config);
    }
    
    auto bench_end = std::chrono::high_resolution_clock::now();
    auto bench_duration = std::chrono::duration_cast<std::chrono::microseconds>(bench_end - bench_start);
    
    std::cout << "Parsed " << ITERATIONS << " configurations in " << bench_duration.count() << " microseconds" << std::endl;
    std::cout << "Average: " << (bench_duration.count() / ITERATIONS) << " microseconds per parse" << std::endl;
    std::cout << "Throughput: " << (ITERATIONS * 1000000.0 / bench_duration.count()) << " parses/second" << std::endl;
    
    // Cleanup
    cfgpp_value_destroy(config_root);
    cfgpp_parser_destroy(parser);
    
    std::cout << std::endl;
    std::cout << "Example completed successfully!" << std::endl;
    
    return 0;
}
