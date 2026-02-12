#include <iostream>
#include <iomanip>
#include <cstdint>

#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

#define I2C_BUS "/dev/i2c-1"
#define SENSOR_ADDR 0x76 // Sensor Address.
#define REG_ID 0xD0 // Chip ID Register.

int main() {
    int file;

    // Open I2C Bus.
    file = open(I2C_BUS, O_RDWR);
    if (file < 0) {
        std:cerr << "Failed to open the I2C bus\n";
        return 1;
    }

    // Connect to the sensor.
    if (ioctl(file, I2C_SLAVE, SENSOR_ADDR) < 0) {
        std:cerr << "Failed to connect to the sensor\n";
        return 1;
    }

    // Write register address to read from.
    uint8_t reg = REG_ID;
    if (write(file, &reg, 1) != 1) {
        std:cerr << "Failed to write to the sensor\n";
        close(file);
        return 1;
    }

    // Read a byte.
    uint8_t data;
    if (read(file, &data, 1) != 1) {
        std:cerr << "Failed to read from the sensor\n";
        close(file);
        return 1;
    }

    std::cout << "Register 0x" << std::hex << (int)REG_ID << " = 0x" << std::hex << (int)data << std::endl;
    close(file);
    return 0;
}

// Compile with: g++ main.cpp -o i2c_read
// Run with: ./main