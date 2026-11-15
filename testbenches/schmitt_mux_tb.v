`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 15:20:52
// Design Name: 
// Module Name: schmitt_mux_tb
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

module schmitt_mux_tb;

    reg [9:0] gpio_inputs;
    reg [3:0] channel_select;

    wire selected_pin;

    integer i;
    integer errors;

    schmitt_mux uut (
        .gpio_inputs(gpio_inputs),
        .channel_select(channel_select),
        .selected_pin(selected_pin)
    );

    initial begin

        $display("--------------------------------");
        $display("SCHMITT GPIO MUX TEST");
        $display("--------------------------------");

        errors = 0;

        // Each GPIO has a unique test value
        gpio_inputs = 10'b1010101010;

        for (i = 0; i < 10; i = i + 1) begin

            channel_select = i;
            #10;

            $display(
                "GPIO %0d selected = %b",
                i,
                selected_pin
            );

            if (selected_pin !== gpio_inputs[i]) begin
                $display("ERROR: GPIO %0d selection failed", i);
                errors = errors + 1;
            end
            else begin
                $display("PASS: GPIO %0d", i);
            end

        end

        // Invalid channel test
        channel_select = 4'd10;
        #10;

        if (selected_pin === 1'b0)
            $display("PASS: Invalid channel handled");
        else begin
            $display("ERROR: Invalid channel was not handled");
            errors = errors + 1;
        end

        $display("--------------------------------");

        if (errors == 0)
            $display("TEST_RESULT: PASS");
        else
            $display("TEST_RESULT: FAIL");

        $finish;

    end

endmodule
