`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 16:04:10
// Design Name: 
// Module Name: pairwise_response
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

module pairwise_response (
    input  wire [239:0] period_values,
    output reg  [44:0]  response
);

    integer i;
    integer j;
    integer k;

    always @(*) begin

        response = 45'd0;
        k = 0;

        for (i = 0; i < 10; i = i + 1) begin

            for (j = i + 1; j < 10; j = j + 1) begin

                if (period_values[i*24 +: 24] >
                    period_values[j*24 +: 24])
                    response[k] = 1'b1;
                else
                    response[k] = 1'b0;

                k = k + 1;

            end

        end

    end

endmodule