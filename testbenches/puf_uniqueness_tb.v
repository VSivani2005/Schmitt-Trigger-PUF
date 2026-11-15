`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 16:26:25
// Design Name: 
// Module Name: puf_uniqueness_tb
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

module puf_uniqueness_tb;

    reg [239:0] periods_A;
    reg [239:0] periods_B;

    wire [44:0] response_A;
    wire [44:0] response_B;

    integer i;
    integer hamming_distance;
    integer uniqueness_x100;

    // Device A pairwise response
    pairwise_response device_A (
        .period_values(periods_A),
        .response(response_A)
    );

    // Device B pairwise response
    pairwise_response device_B (
        .period_values(periods_B),
        .response(response_B)
    );

    initial begin

        $display("==========================================");
        $display("TWO-DEVICE PUF UNIQUENESS TEST");
        $display("==========================================");

        // Simulated measurements for Device A
        periods_A[0*24 +: 24] = 24'd10;
        periods_A[1*24 +: 24] = 24'd15;
        periods_A[2*24 +: 24] = 24'd12;
        periods_A[3*24 +: 24] = 24'd23;
        periods_A[4*24 +: 24] = 24'd21;
        periods_A[5*24 +: 24] = 24'd30;
        periods_A[6*24 +: 24] = 24'd27;
        periods_A[7*24 +: 24] = 24'd43;
        periods_A[8*24 +: 24] = 24'd39;
        periods_A[9*24 +: 24] = 24'd47;

        // Simulated measurements for Device B
        periods_B[0*24 +: 24] = 24'd19;
        periods_B[1*24 +: 24] = 24'd55;
        periods_B[2*24 +: 24] = 24'd43;
        periods_B[3*24 +: 24] = 24'd13;
        periods_B[4*24 +: 24] = 24'd28;
        periods_B[5*24 +: 24] = 24'd25;
        periods_B[6*24 +: 24] = 24'd58;
        periods_B[7*24 +: 24] = 24'd16;
        periods_B[8*24 +: 24] = 24'd37;
        periods_B[9*24 +: 24] = 24'd49;

        #10;

        $display("\nDEVICE A PERIODS:");

        for (i = 0; i < 10; i = i + 1)
            $display("GPIO %0d = %0d cycles",
                i, periods_A[i*24 +: 24]);

        $display("\nDEVICE B PERIODS:");

        for (i = 0; i < 10; i = i + 1)
            $display("GPIO %0d = %0d cycles",
                i, periods_B[i*24 +: 24]);

        $display("\nDEVICE A RESPONSE:");
        $display("%045b", response_A);

        $display("\nDEVICE B RESPONSE:");
        $display("%045b", response_B);

        // Calculate Hamming distance
        hamming_distance = 0;

        for (i = 0; i < 45; i = i + 1) begin
            if (response_A[i] != response_B[i])
                hamming_distance = hamming_distance + 1;
        end

        // Calculate normalized difference in hundredths of a percent
        uniqueness_x100 =
            (hamming_distance * 10000 + 22) / 45;

        $display("\n==========================================");
        $display("UNIQUENESS ANALYSIS");
        $display("==========================================");

        $display("Total response bits = 45");
        $display("Different bits = %0d", hamming_distance);
        $display("Matching bits = %0d",
                 45 - hamming_distance);

        $display("Hamming distance = %0d",
                 hamming_distance);

        $display("Inter-device difference = %0d.%02d%%",
                 uniqueness_x100 / 100,
                 uniqueness_x100 % 100);

        $display("==========================================");

        if (hamming_distance == 22) begin
            $display("PASS: Expected Hamming distance of 22 verified");
            $display("TEST_RESULT: PASS");
        end
        else begin
            $display("FAIL: Expected Hamming distance 22, received %0d",
                     hamming_distance);
            $display("TEST_RESULT: FAIL");
        end

        $display("TWO-DEVICE COMPARISON COMPLETED");
        $display("==========================================");

        $finish;

    end

endmodule
