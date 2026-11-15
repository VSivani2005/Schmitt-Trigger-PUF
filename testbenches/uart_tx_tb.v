`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 15:46:17
// Design Name: 
// Module Name: uart_tx_tb
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

module uart_tx_tb;

    reg clk;
    reg rst;
    reg [7:0] tx_data;
    reg tx_start;

    wire tx_serial;
    wire tx_busy;
    wire tx_done;

    localparam integer BIT_TIME = 8700;

    integer byte_count;

    uart_tx uut (
        .clk(clk),
        .rst(rst),
        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx_serial(tx_serial),
        .tx_busy(tx_busy),
        .tx_done(tx_done)
    );

    // 10 MHz clock
    always #5 clk = ~clk;

    // Send one byte and wait for completion
    task transmit_byte;
        input [7:0] data;
        begin
            @(negedge clk);
            tx_data = data;
            tx_start = 1'b1;

            @(negedge clk);
            tx_start = 1'b0;

            wait (tx_done == 1'b1);
            #1;

            byte_count = byte_count + 1;

            $display("Byte %0d transmitted = 0x%02h",
                     byte_count, data);

            @(negedge clk);
        end
    endtask

    initial begin
        clk = 0;
        rst = 1;
        tx_data = 0;
        tx_start = 0;
        byte_count = 0;

        $display("----------------------------------");
        $display("UART TRANSMITTER TEST");
        $display("----------------------------------");

        repeat (5) @(negedge clk);
        rst = 0;

        // Example 24-bit measurement: 0x123456
        $display("Transmitting 24-bit value: 0x123456");

        transmit_byte(8'h12);
        transmit_byte(8'h34);
        transmit_byte(8'h56);

        if (byte_count == 3) begin
            $display("PASS: All three bytes transmitted");
            $display("TEST_RESULT: PASS");
        end
        else begin
            $display("FAIL: Expected 3 bytes, transmitted %0d",
                     byte_count);
            $display("TEST_RESULT: FAIL");
        end

        $display("----------------------------------");
        #100;
        $finish;
    end

    initial begin
        #1000000;
        if (byte_count < 3) begin
            $display("FAIL: UART transmitter simulation timeout");
            $display("TEST_RESULT: TIMEOUT");
            $finish;
        end
    end

endmodule
