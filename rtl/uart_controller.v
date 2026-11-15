`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 15:50:18
// Design Name: 
// Module Name: uart_controller
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

module uart_controller (
    input  wire        clk,
    input  wire        rst,

    // UART receiver interface
    input  wire [7:0]  rx_data,
    input  wire        rx_dv,

    // GPIO selection interface
    output reg  [3:0]  channel_select,

    // Period measurement interface
    output reg         req_meas,
    input  wire [23:0] period_data,
    input  wire        ack_meas,

    // UART transmitter interface
    output reg  [7:0]  tx_data,
    output reg         tx_start,
    input  wire        tx_busy,
    input  wire        tx_done
);

    localparam IDLE       = 4'd0;
    localparam WAIT_GPIO  = 4'd1;
    localparam MEASURE    = 4'd2;
    localparam SEND_BYTE1 = 4'd3;
    localparam WAIT_BYTE1 = 4'd4;
    localparam SEND_BYTE2 = 4'd5;
    localparam WAIT_BYTE2 = 4'd6;
    localparam SEND_BYTE3 = 4'd7;
    localparam WAIT_BYTE3 = 4'd8;

    reg [3:0] state;
    reg [23:0] result_buffer;

    always @(posedge clk) begin

        if (rst) begin
            state          <= IDLE;
            channel_select <= 4'd0;
            req_meas       <= 1'b0;
            tx_data        <= 8'd0;
            tx_start       <= 1'b0;
            result_buffer  <= 24'd0;
        end

        else begin

            // Default: one-clock transmitter start pulse
            tx_start <= 1'b0;

            case (state)

                IDLE: begin
                    req_meas <= 1'b0;

                    // Wait for measurement command 10
                    if (rx_dv && rx_data == 8'd10)
                        state <= WAIT_GPIO;
                end

                WAIT_GPIO: begin

                    // Wait for the GPIO index
                    if (rx_dv) begin
                        if (rx_data <= 8'd9) begin
                            channel_select <= rx_data[3:0];
                            req_meas <= 1'b1;
                            state <= MEASURE;
                        end
                        else begin
                            state <= IDLE;
                        end
                    end
                end

                MEASURE: begin

                    // Wait for period measurement completion
                    if (ack_meas) begin
                        result_buffer <= period_data;
                        req_meas <= 1'b0;
                        state <= SEND_BYTE1;
                    end
                end

                SEND_BYTE1: begin
                    if (!tx_busy) begin
                        tx_data <= result_buffer[23:16];
                        tx_start <= 1'b1;
                        state <= WAIT_BYTE1;
                    end
                end

                WAIT_BYTE1: begin
                    if (tx_done)
                        state <= SEND_BYTE2;
                end

                SEND_BYTE2: begin
                    if (!tx_busy) begin
                        tx_data <= result_buffer[15:8];
                        tx_start <= 1'b1;
                        state <= WAIT_BYTE2;
                    end
                end

                WAIT_BYTE2: begin
                    if (tx_done)
                        state <= SEND_BYTE3;
                end

                SEND_BYTE3: begin
                    if (!tx_busy) begin
                        tx_data <= result_buffer[7:0];
                        tx_start <= 1'b1;
                        state <= WAIT_BYTE3;
                    end
                end

                WAIT_BYTE3: begin
                    if (tx_done)
                        state <= IDLE;
                end

                default: begin
                    state <= IDLE;
                    req_meas <= 1'b0;
                    tx_start <= 1'b0;
                end

            endcase
        end
    end

    initial begin
        state = IDLE;
        channel_select = 4'd0;
        req_meas = 1'b0;
        tx_data = 8'd0;
        tx_start = 1'b0;
        result_buffer = 24'd0;
    end

endmodule