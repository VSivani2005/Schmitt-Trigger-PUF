`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 15:33:06
// Design Name: 
// Module Name: uart_rx
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

module uart_rx #(
    parameter integer CLK_FREQ = 100000000,
    parameter integer BAUD_RATE = 115200
)(
    input  wire       clk,
    input  wire       rst,
    input  wire       rx_serial,

    output reg [7:0]  rx_data,
    output reg        rx_dv
);

    localparam integer CLKS_PER_BIT =
        (CLK_FREQ + BAUD_RATE/2) / BAUD_RATE;

    localparam IDLE  = 2'b00;
    localparam START = 2'b01;
    localparam DATA  = 2'b10;
    localparam STOP  = 2'b11;

    reg [1:0] state;
    reg [15:0] clk_count;
    reg [2:0] bit_index;

    // Synchronize the asynchronous UART input
    reg rx_sync_1;
    reg rx_sync_2;

    always @(posedge clk) begin
        if (rst) begin
            rx_sync_1 <= 1'b1;
            rx_sync_2 <= 1'b1;
        end
        else begin
            rx_sync_1 <= rx_serial;
            rx_sync_2 <= rx_sync_1;
        end
    end

    always @(posedge clk) begin
        if (rst) begin
            state     <= IDLE;
            clk_count <= 0;
            bit_index <= 0;
            rx_data   <= 0;
            rx_dv     <= 0;
        end
        else begin
            rx_dv <= 1'b0;

            case (state)

                IDLE: begin
                    clk_count <= 0;
                    bit_index <= 0;

                    if (rx_sync_2 == 1'b0)
                        state <= START;
                end

                START: begin
                    if (clk_count == (CLKS_PER_BIT/2 - 1)) begin
                        clk_count <= 0;

                        if (rx_sync_2 == 1'b0)
                            state <= DATA;
                        else
                            state <= IDLE;
                    end
                    else begin
                        clk_count <= clk_count + 1'b1;
                    end
                end

                DATA: begin
                    if (clk_count == CLKS_PER_BIT - 1) begin
                        clk_count <= 0;
                        rx_data[bit_index] <= rx_sync_2;

                        if (bit_index == 3'd7) begin
                            bit_index <= 0;
                            state <= STOP;
                        end
                        else begin
                            bit_index <= bit_index + 1'b1;
                        end
                    end
                    else begin
                        clk_count <= clk_count + 1'b1;
                    end
                end

                STOP: begin
                    if (clk_count == CLKS_PER_BIT - 1) begin
                        clk_count <= 0;
                        rx_dv <= 1'b1;
                        state <= IDLE;
                    end
                    else begin
                        clk_count <= clk_count + 1'b1;
                    end
                end

                default: begin
                    state <= IDLE;
                    clk_count <= 0;
                    bit_index <= 0;
                end

            endcase
        end
    end

endmodule