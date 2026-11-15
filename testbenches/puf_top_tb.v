`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 15:57:40
// Design Name: 
// Module Name: puf_top_tb
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


`timescale 1ns / 1ps

module puf_top_tb;

    reg clk;
    reg rst;

    reg uart_rx_pin;
    wire uart_tx_pin;

    reg [9:0] gpio_inputs;

    wire [7:0] monitor_data;
    wire monitor_dv;

    integer rx_count;
    integer errors;

    reg [7:0] result_byte1;
    reg [7:0] result_byte2;
    reg [7:0] result_byte3;

    localparam integer BIT_TIME = 8680;

    // Device under test
    puf_top uut (
        .clk(clk),
        .rst(rst),
        .uart_rx_pin(uart_rx_pin),
        .uart_tx_pin(uart_tx_pin),
        .gpio_inputs(gpio_inputs)
    );

    // UART receiver used to monitor the DUT's serial output
    uart_rx monitor (
        .clk(clk),
        .rst(rst),
        .rx_serial(uart_tx_pin),
        .rx_data(monitor_data),
        .rx_dv(monitor_dv)
    );

    // 10 MHz clock
    always #5 clk = ~clk;

    // Simulated oscillating GPIO 7
    always #500 gpio_inputs[7] = ~gpio_inputs[7];

    // Send one byte to the FPGA using UART
    task send_uart_byte;
        input [7:0] data;
        integer b;
        begin
            uart_rx_pin = 1'b0;
            #(BIT_TIME);

            for (b = 0; b < 8; b = b + 1) begin
                uart_rx_pin = data[b];
                #(BIT_TIME);
            end

            uart_rx_pin = 1'b1;
            #(BIT_TIME);
        end
    endtask

    // Monitor bytes returned by the FPGA
    always @(posedge clk) begin
        if (!rst && monitor_dv) begin

            rx_count = rx_count + 1;

            case (rx_count)

                1: result_byte1 = monitor_data;
                2: result_byte2 = monitor_data;
                3: result_byte3 = monitor_data;

            endcase

            $display("FPGA returned byte %0d = 0x%02h",
                     rx_count, monitor_data);
        end
    end

    initial begin

        clk = 0;
        rst = 1;

        uart_rx_pin = 1'b1;
        gpio_inputs = 10'b0000000000;

        rx_count = 0;
        errors = 0;

        result_byte1 = 0;
        result_byte2 = 0;
        result_byte3 = 0;

        $display("----------------------------------");
        $display("COMPLETE SCHMITT PUF RTL TEST");
        $display("----------------------------------");

        // Reset the design
        repeat (10) @(negedge clk);
        rst = 0;

        // Send command byte
        $display("Sending command: 10");
        send_uart_byte(8'd10);

        // Send GPIO channel
        $display("Sending GPIO selection: 7");
        send_uart_byte(8'd7);

        // Wait for all three result bytes
        wait (rx_count == 3);

        #200;

        $display("----------------------------------");
        $display("RESULT VERIFICATION");
        $display("----------------------------------");

        $display("Received 24-bit result = 0x%02h%02h%02h",
                 result_byte1, result_byte2, result_byte3);

        if ({result_byte1, result_byte2, result_byte3} != 24'd0)
            $display("PASS: Non-zero measurement returned");
        else begin
            $display("FAIL: Measurement result is zero");
            errors = errors + 1;
        end

        if (uut.channel_select == 4'd7)
            $display("PASS: Correct GPIO channel selected");
        else begin
            $display("FAIL: Incorrect GPIO channel");
            errors = errors + 1;
        end        if (errors == 0) begin
            $display("PASS: COMPLETE RTL INTEGRATION TEST");
            $display("TEST_RESULT: PASS");
        end
        else begin
            $display("FAIL: Integration errors = %0d", errors);
            $display("TEST_RESULT: FAIL");
        end

        $display("----------------------------------");

        #100;
        $finish;
    end

    // Watchdog: prevent an endless simulation if a response is missing
    initial begin
        #1000000;

        if (rx_count < 3) begin
            $display("FAIL: Timeout waiting for UART response");
            $display("TEST_RESULT: TIMEOUT");
            $finish;
        end
    end

endmodule
