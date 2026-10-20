module testbench();
wire [15:0]S;
reg [7:0]a,b;
//Reorder uut(a,b,S);
Appox_8bit_ORed uut(S,a,b);
//Exact_8bit uut(b,a,S);
initial
begin
	a = 8'd237;
	b = 8'd167;

#200;
	a = 8'd167;
	b = 8'd237;

end
endmodule 
