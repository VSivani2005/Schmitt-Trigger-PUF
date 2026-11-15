`timescale 1ns / 1ps

module period_measurement_tb;

    reg clk_100mhz;
    reg rst;
    reg req_meas;
    reg pin_selected;
    reg completed;

    wire pin_out;
    wire [23:0] data_out;
    wire ack_meas;
    wire busy;

    period_measurement uut (
        .clk_100mhz(clk_100mhz),
        .rst(rst),
        .req_meas(req_meas),
        .pin_selected(pin_selected),
        .pin_out(pin_out),
        .data_out(data_out),
        .ack_meas(ack_meas),
        .busy(busy)
    );

    always #5 clk_100mhz = ~clk_100mhz;

    // Generate a 1 us oscillation period
    initial begin
        #100;
        forever begin
            #500 pin_selected = 1'b1;
            #500 pin_selected = 1'b0;
        end
    end

    // Independent timeout
    initial begin
        #10000;
        if (!completed) begin
            $display("FAIL: Measurement timeout");
            $display("TEST_RESULT: TIMEOUT");
            $finish;
        end
    end

    initial begin
        clk_100mhz = 0;
        rst = 1;
        req_meas = 0;
        pin_selected = 0;
        completed = 0;

        $display("----------------------------------");
        $display("GPIO SCHMITT PUF - PERIOD TEST");
        $display("----------------------------------");

        #50;
        rst = 0;

        #150;
        req_meas = 1;
        $display("Measurement request started");

        wait (ack_meas == 1'b1);
        #1;

        completed = 1;

        $display("Measured clock cycles = %d", data_out);
        $display("Measurement ACK received");

        @(negedge clk_100mhz);
        req_meas = 0;

        #100;

        if (data_out == 24'd100) begin
            $display("PASS: Expected period measurement obtained");
            $display("TEST_RESULT: PASS");
        end
        else begin
            $display("FAIL: Expected 100, received %d", data_out);
            $display("TEST_RESULT: FAIL");
        end

        $display("----------------------------------");
        $finish;
    end

endmodule
