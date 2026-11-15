`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.11.2026 15:56:37
// Design Name: 
// Module Name: puf_top
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

module puf_top (
    input  wire        clk,
    input  wire        rst,

    input  wire        uart_rx_pin,
    output wire        uart_tx_pin,

    input  wire [9:0]  gpio_inputs,

    // External RC feedback connection
    output wire        rc_feedback_out
);

    // UART receiver signals
    wire [7:0] rx_data;
    wire       rx_dv;

    // GPIO multiplexer signals
    wire [3:0] channel_select;
    wire       selected_pin;

    // Period measurement signals
    wire        req_meas;
    wire [23:0] period_data;
    wire        ack_meas;
    wire        busy;
    wire        feedback_out;

    // UART transmitter signals
    wire [7:0] tx_data;
    wire       tx_start;
    wire       tx_busy;
    wire       tx_done;

    // 1. UART Receiver
    // Basys 3 onboard clock = 100 MHz
    uart_rx #(
        .CLK_FREQ(100000000),
        .BAUD_RATE(115200)
    ) uart_receiver (
        .clk(clk),
        .rst(rst),
        .rx_serial(uart_rx_pin),
        .rx_data(rx_data),
        .rx_dv(rx_dv)
    );

    // 2. UART Controller
    uart_controller controller (
        .clk(clk),
        .rst(rst),

        .rx_data(rx_data),
        .rx_dv(rx_dv),

        .channel_select(channel_select),

        .req_meas(req_meas),
        .period_data(period_data),
        .ack_meas(ack_meas),

        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx_busy(tx_busy),
        .tx_done(tx_done)
    );

    // 3. Ten-input GPIO Multiplexer
    schmitt_mux gpio_mux (
        .gpio_inputs(gpio_inputs),
        .channel_select(channel_select),
        .selected_pin(selected_pin)
    );

    // 4. Period Measurement
    // Measurement clock = 100 MHz
   period_measurement period_counter (
    .clk_100mhz(clk),
    .rst(rst),
    .req_meas(req_meas),
    .pin_selected(selected_pin),
    .pin_out(feedback_out),
    .data_out(period_data),
    .ack_meas(ack_meas),
    .busy(busy)
);
    // 5. UART Transmitter
    uart_tx #(
        .CLK_FREQ(100000000),
        .BAUD_RATE(115200)
    ) uart_transmitter (
        .clk(clk),
        .rst(rst),
        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx_serial(uart_tx_pin),
        .tx_busy(tx_busy),
        .tx_done(tx_done)
    );

    // Expose feedback output to the physical RC circuit
    assign rc_feedback_out = feedback_out;

endmodule
