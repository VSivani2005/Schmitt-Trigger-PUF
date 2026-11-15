`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 16:10:13
// Design Name: 
// Module Name: multi_gpio_measurement_tb
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

module multi_gpio_measurement_tb;

    reg clk = 0;
    reg rst = 1'b1;
    reg [9:0] gpio_inputs = 10'b0;

    reg [3:0] channel_select = 0;
    reg req_meas = 0;

    wire selected_pin;
    wire feedback_out;

    wire [23:0] measured_period;
    wire ack_meas;
    wire busy;

    reg [239:0] period_values = 240'd0;
    wire [44:0] response;

    integer i;
    integer j;
    integer errors;

    // 10 MHz simulation clock
    always #5 clk = ~clk;

    // Ten GPIO signals with different simulated timings
   always #525  gpio_inputs[0] = ~gpio_inputs[0];
   always #725  gpio_inputs[1] = ~gpio_inputs[1];
   always #625  gpio_inputs[2] = ~gpio_inputs[2];
   always #1125 gpio_inputs[3] = ~gpio_inputs[3];
   always #1025 gpio_inputs[4] = ~gpio_inputs[4];
   always #1525 gpio_inputs[5] = ~gpio_inputs[5];
   always #1325 gpio_inputs[6] = ~gpio_inputs[6];
   always #2125 gpio_inputs[7] = ~gpio_inputs[7];
   always #1925 gpio_inputs[8] = ~gpio_inputs[8];
   always #2325 gpio_inputs[9] = ~gpio_inputs[9];

    // GPIO selection
    schmitt_mux mux_inst (
        .gpio_inputs(gpio_inputs),
        .channel_select(channel_select),
        .selected_pin(selected_pin)
    );

    // Period measurement
    period_measurement measurement_inst (
        .clk_100mhz(clk),
         .rst(rst),
        .req_meas(req_meas),
        .pin_selected(selected_pin),
        .pin_out(feedback_out),
        .data_out(measured_period),
        .ack_meas(ack_meas),
        .busy(busy)
    );

    // Pairwise response generation
    pairwise_response response_inst (
        .period_values(period_values),
        .response(response)
    );

    // Measure one selected GPIO
    task measure_channel;
        input integer idx;

        begin
            @(negedge clk);

            channel_select = idx;

            // Allow the selected signal to settle
            repeat (2) @(negedge clk);

            req_meas = 1'b1;

            // Wait for the measurement to complete
            wait (ack_meas == 1'b1);

            // Store the measured period
            period_values[idx*24 +: 24] = measured_period;

            @(negedge clk);
            req_meas = 1'b0;

            // Allow the measurement module to return to IDLE
            repeat (2) @(negedge clk);
        end
    endtask

    initial begin

        $display("------------------------------------------");
        $display("MULTI-GPIO PUF MEASUREMENT TEST");
        $display("------------------------------------------");

        repeat (5) @(negedge clk);
        rst = 1'b0;

        // Measure all ten GPIO inputs
        for (i = 0; i < 10; i = i + 1) begin

            measure_channel(i);

            $display(
                "GPIO %0d measured period = %0d cycles",
                i, period_values[i*24 +: 24]
            );

        end

        #1;

        $display("\n------------------------------------------");
        $display("MEASURED PERIOD SUMMARY");
        $display("------------------------------------------");

        errors = 0;

        // Check for zero or duplicate measurements
        for (i = 0; i < 10; i = i + 1) begin

            if (period_values[i*24 +: 24] == 0) begin
                $display("ERROR: GPIO %0d has zero measurement", i);
                errors = errors + 1;
            end

            for (j = i + 1; j < 10; j = j + 1) begin

                if (period_values[i*24 +: 24] ==
                    period_values[j*24 +: 24]) begin

                    $display(
                        "WARNING: GPIO %0d and GPIO %0d have equal periods",
                        i, j
                    );

                    errors = errors + 1;
                end

            end

        end

        $display("\nGenerated 45-bit response:");
        $display("%045b", response);

        $display("\n------------------------------------------");
        $display("FINAL VERIFICATION");
        $display("------------------------------------------");

        if (errors == 0) begin
            $display("PASS: All ten GPIO periods are non-zero and distinct");
            $display("PASS: Pairwise response generated");
            $display("TEST_RESULT: PASS");
        end
        else begin
            $display("FAIL: Measurement errors = %0d", errors);
            $display("TEST_RESULT: FAIL");
        end

        $display("------------------------------------------");

        $finish;

    end

    // Simulation watchdog
    initial begin
        #200000;
        $display("ERROR: Simulation timeout");
        $display("TEST_RESULT: TIMEOUT");
        $finish;
    end

endmodule