`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 16:05:37
// Design Name: 
// Module Name: pairwise_puf_tb
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

module pairwise_puf_tb;

    reg [239:0] period_values;
    wire [44:0] response;

    integer i;
    integer j;
    integer k;
    integer ones_count;
    integer zeros_count;
    integer errors;

    reg expected_bit;

    pairwise_response uut (
        .period_values(period_values),
        .response(response)
    );

    initial begin

        $display("------------------------------------------");
        $display("10-GPIO PAIRWISE PUF RESPONSE TEST");
        $display("------------------------------------------");

        // Simulated period values in nanoseconds
        period_values[0*24 +: 24] = 24'd100;
        period_values[1*24 +: 24] = 24'd140;
        period_values[2*24 +: 24] = 24'd120;
        period_values[3*24 +: 24] = 24'd180;
        period_values[4*24 +: 24] = 24'd160;
        period_values[5*24 +: 24] = 24'd220;
        period_values[6*24 +: 24] = 24'd200;
        period_values[7*24 +: 24] = 24'd260;
        period_values[8*24 +: 24] = 24'd240;
        period_values[9*24 +: 24] = 24'd280;

        #10;

        k = 0;
        ones_count = 0;
        zeros_count = 0;
        errors = 0;

        $display("\nGPIO period measurements:");

        for (i = 0; i < 10; i = i + 1) begin
            $display("GPIO %0d = %0d ns",
                     i, period_values[i*24 +: 24]);
        end

        $display("\nPairwise comparisons:");

        for (i = 0; i < 10; i = i + 1) begin

            for (j = i + 1; j < 10; j = j + 1) begin

                if (period_values[i*24 +: 24] >
                    period_values[j*24 +: 24])
                    expected_bit = 1'b1;
                else
                    expected_bit = 1'b0;

                $display("GPIO %0d vs GPIO %0d : Response = %b",
                         i, j, response[k]);

                if (response[k] !== expected_bit) begin
                    $display("ERROR: Pair %0d,%0d", i, j);
                    errors = errors + 1;
                end

                if (response[k] == 1'b1)
                    ones_count = ones_count + 1;
                else
                    zeros_count = zeros_count + 1;

                k = k + 1;

            end

        end

        $display("\n------------------------------------------");
        $display("PAIRWISE RESPONSE SUMMARY");
        $display("------------------------------------------");

        $display("Total comparisons = %0d", k);
        $display("Response 1 count = %0d", ones_count);
        $display("Response 0 count = %0d", zeros_count);
        $display("Generated response = %045b", response);

        if (k == 45 && errors == 0) begin
            $display("PASS: All 45 pairwise comparisons verified");
            $display("TEST_RESULT: PASS");
        end
        else begin
            $display("FAIL: Pairwise comparison errors = %0d",
                     errors);
            $display("TEST_RESULT: FAIL");
        end

        $display("------------------------------------------");

        $finish;

    end

endmodule
