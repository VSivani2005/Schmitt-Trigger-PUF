`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 15:07:39
// Design Name: 
// Module Name: period_measurement
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:9// 
//////////////////////////////////////////////////////////////////////////////////



`timescale 1ns / 1ps

module period_measurement (
    input  wire        clk_100mhz,
    input  wire        rst,
    input  wire        req_meas,
    input  wire        pin_selected,

    output wire        pin_out,
    output reg  [23:0] data_out,
    output reg         ack_meas,
    output reg         busy
);

    localparam IDLE       = 2'b00;
    localparam WAIT_FIRST = 2'b01;
    localparam MEASURE    = 2'b10;

    reg [1:0] state;
    reg [23:0] period_counter;

    // Asynchronous feedback signal synchronizer
    reg pin_sync_1;
    reg pin_sync_2;
    reg pin_prev;

    // Preserve direct feedback for the external RC circuit
    assign pin_out = ~pin_selected;

    // Two-stage synchronization and measurement FSM
    always @(posedge clk_100mhz) begin

        if (rst) begin
            state          <= IDLE;
            period_counter <= 24'd0;
            data_out       <= 24'd0;
            ack_meas       <= 1'b0;
            busy           <= 1'b0;

            pin_sync_1     <= 1'b0;
            pin_sync_2     <= 1'b0;
            pin_prev       <= 1'b0;
        end

        else begin

            // Synchronize feedback for measurement only
            pin_sync_1 <= pin_out;
            pin_sync_2 <= pin_sync_1;
            pin_prev   <= pin_sync_2;

            // Default acknowledgement
            ack_meas <= 1'b0;

            case (state)

                IDLE: begin
                    busy           <= 1'b0;
                    period_counter <= 24'd0;

                    if (req_meas) begin
                        busy     <= 1'b1;
                        data_out <= 24'd0;
                        state    <= WAIT_FIRST;
                    end
                end

                WAIT_FIRST: begin

                    if (!req_meas) begin
                        state <= IDLE;
                        busy  <= 1'b0;
                    end

                    else if (pin_sync_2 && !pin_prev) begin
                        period_counter <= 24'd0;
                        state <= MEASURE;
                    end
                end

                MEASURE: begin

                    if (!req_meas) begin
                        state <= IDLE;
                        busy  <= 1'b0;
                    end

                    else if (pin_sync_2 && !pin_prev) begin

                        data_out <= period_counter + 24'd1;

                        ack_meas <= 1'b1;
                        busy     <= 1'b0;

                        state <= IDLE;
                    end

                    else begin
                        period_counter <= period_counter + 24'd1;
                    end
                end

                default: begin
                    state <= IDLE;
                    busy  <= 1'b0;
                end

            endcase
        end
    end

endmodule
