/******
Demo for ssd1306 i2c driver for Raspberry Pi
******/
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include "ssd1306_i2c.h"

#define DEBUG 0

#define DISTINCT_DISPLAYS 6
#define SECONDS_TO_DISPLAY 3

static unsigned char select_display(void)
{
    struct timespec now;
    clock_gettime(CLOCK_REALTIME, &now);

    long slot = now.tv_sec / SECONDS_TO_DISPLAY;          // advances every N seconds
    return (unsigned char)(slot % DISTINCT_DISPLAYS);     // 0..5
}

static void sleep_until_next_change(void)
{
    struct timespec now;
    clock_gettime(CLOCK_REALTIME, &now);

    long next_sec = ((now.tv_sec / SECONDS_TO_DISPLAY) + 1) * SECONDS_TO_DISPLAY;

    struct timespec sleep_ts;
    sleep_ts.tv_sec  = next_sec - now.tv_sec - 1;
    sleep_ts.tv_nsec = 1000000000L - now.tv_nsec;

    // If we're extremely close to the boundary, avoid negative sleep
    if (sleep_ts.tv_sec < 0) {
        sleep_ts.tv_sec = 0;
        sleep_ts.tv_nsec = 0;
    }

    nanosleep(&sleep_ts, NULL);
}

int main(void)
{
    ssd1306_begin(SSD1306_SWITCHCAPVCC, SSD1306_I2C_ADDRESS); // LCD init
    if (i2cd < 0) {
        fprintf(stderr, "I2C device failed to open\r\n");
        return 0;
    }

    usleep(150 * 1000);
    FirstGetIpAddress();

    while (1) {
        unsigned char symbol = select_display();
        if (DEBUG) { printf("Display=%u\n", symbol); fflush(stdout); }

        LCD_Display(symbol);
        sleep_until_next_change();
    }

    return 0;
}
