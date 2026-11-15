`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 15:51:56
// Design Name: 
// Module Name: uart_controller_tb
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

module uart_controller_tb;

    reg clk;
    reg rst;

    reg [7:0] rx_data;
    reg rx_dv;

    wire [3:0] channel_select;

    wire req_meas;
    reg [23:0] period_data;
    reg ack_meas;

    wire [7:0] tx_data;
    wire tx_start;
    reg tx_busy;
    reg tx_done;

    integer tx_count;
    integer errors;
    integer delay_count;

    uart_controller uut (
        .clk(clk),
        .rst(rst),

        .rx_data(rx_data),
        .rx_dv(rx_dv),

        .channel_select(channel_select),

        .req_meas(req_meas),
        .period_data(period_data),
        .ack_meas(ack_meas),

        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx_busy(tx_busy),
        .tx_done(tx_done)
    );

    always #50 clk = ~clk;

    // Send a simulated received UART byte to the controller
    task send_command_byte;
        input [7:0] data;
        begin
            @(negedge clk);
            rx_data = data;
            rx_dv = 1'b1;

            @(negedge clk);
            rx_dv = 1'b0;
        end
    endtask

    // Simulated transmitter handshake
    // This verifies controller sequencing, not the serial waveform.
    always @(posedge clk) begin
        if (rst) begin
            tx_busy <= 1'b0;
            tx_done <= 1'b0;
            delay_count <= 0;
            tx_count <= 0;
        end
        else begin
            tx_done <= 1'b0;

            if (tx_start && !tx_busy) begin
                tx_busy <= 1'b1;
                delay_count <= 5;

                tx_count <= tx_count + 1;

                $display("Controller sends byte %0d = 0x%02h",
                         tx_count + 1, tx_data);

                if (tx_count == 0 && tx_data !== 8'h12)
                    errors <= errors + 1;

                if (tx_count == 1 && tx_data !== 8'h34)
                    errors <= errors + 1;

                if (tx_count == 2 && tx_data !== 8'h56)
                    errors <= errors + 1;
            end

            else if (tx_busy) begin
                if (delay_count == 0) begin
                    tx_busy <= 1'b0;
                    tx_done <= 1'b1;
                end
                else begin
                    delay_count <= delay_count - 1;
                end
            end
        end
    end

    initial begin
        clk = 0;
        rst = 1;

        rx_data = 0;
        rx_dv = 0;

        period_data = 24'h123456;
        ack_meas = 0;

        tx_busy = 0;
        tx_done = 0;

        tx_count = 0;
        errors = 0;
        delay_count = 0;

        $display("----------------------------------");
        $display("UART CONTROLLER TEST");
        $display("----------------------------------");

        repeat (5) @(negedge clk);
        rst = 0;

        // Send measurement command
        $display("Sending command: 10");
        send_command_byte(8'd10);

        // Send GPIO selection
        $display("Sending GPIO selection: 7");
        send_command_byte(8'd7);

        wait (req_meas == 1'b1);

        if (channel_select == 4'd7)
            $display("PASS: GPIO 7 selected");
        else begin
            $display("FAIL: Incorrect GPIO selection");
            errors = errors + 1;
        end

        // Simulate period measurement completion
        $display("Measurement started");

        repeat (20) @(negedge clk);
        ack_meas = 1'b1;

        @(negedge clk);
        ack_meas = 1'b0;

        wait (tx_count == 3);
        wait (tx_done == 1'b1);
        @(negedge clk);

        if (errors == 0 && tx_count == 3) begin
            $display("PASS: UART controller test completed");
            $display("TEST_RESULT: PASS");
        end
        else begin
            $display("FAIL: Controller errors = %0d, TX count = %0d",
                     errors, tx_count);
            $display("TEST_RESULT: FAIL");
        end

        $display("----------------------------------");

        #100;
        $finish;
    end

    initial begin
        #1000000;
        $display("FAIL: UART controller simulation timeout");
        $display("TEST_RESULT: TIMEOUT");
        $finish;
    end

endmodule

