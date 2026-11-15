`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 15:17:31
// Design Name: 
// Module Name: schmitt_mux
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


module schmitt_mux (
    input  wire [9:0] gpio_inputs,
    input  wire [3:0] channel_select,
    output reg        selected_pin
);

    always @(*) begin

        case (channel_select)

            4'd0: selected_pin = gpio_inputs[0];
            4'd1: selected_pin = gpio_inputs[1];
            4'd2: selected_pin = gpio_inputs[2];
            4'd3: selected_pin = gpio_inputs[3];
            4'd4: selected_pin = gpio_inputs[4];
            4'd5: selected_pin = gpio_inputs[5];
            4'd6: selected_pin = gpio_inputs[6];
            4'd7: selected_pin = gpio_inputs[7];
            4'd8: selected_pin = gpio_inputs[8];
            4'd9: selected_pin = gpio_inputs[9];

            default: selected_pin = 1'b0;

        endcase

    end

endmodule

