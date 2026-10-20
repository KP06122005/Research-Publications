module MUL_4(
    input [7:0] a,b,
    output [15:0] S
);

wire [7:0]p[7:0];
	// Partial Products
 	and and_gate0  (p[0][0], b[0], a[0]);
	and and_gate1  (p[0][1], b[0], a[1]);
	and and_gate2  (p[0][2], b[0], a[2]);
	and and_gate3  (p[0][3], b[0], a[3]);
	and and_gate4  (p[0][4], b[0], a[4]);
	and and_gate5  (p[0][5], b[0], a[5]);
	and and_gate6  (p[0][6], b[0], a[6]);
	and and_gate7  (p[0][7], b[0], a[7]);
	
	// Second group Pth b[1] constant
	and and_gate8  (p[1][0], b[1], a[0]);
	and and_gate9  (p[1][1], b[1], a[1]);
	and and_gate10 (p[1][2], b[1], a[2]);
	and and_gate11 (p[1][3], b[1], a[3]);
	and and_gate12 (p[1][4], b[1], a[4]);
	and and_gate13 (p[1][5], b[1], a[5]);
	and and_gate14 (p[1][6], b[1], a[6]);
	and and_gate15 (p[1][7], b[1], a[7]);
	
	// Third group Pth b[2] constant
	and and_gate16 (p[2][0], b[2], a[0]);
	and and_gate17 (p[2][1], b[2], a[1]);
	and and_gate18 (p[2][2], b[2], a[2]);
	and and_gate19 (p[2][3], b[2], a[3]);
	and and_gate20 (p[2][4], b[2], a[4]);
	and and_gate21 (p[2][5], b[2], a[5]);
	and and_gate22 (p[2][6], b[2], a[6]);
	and and_gate23 (p[2][7], b[2], a[7]);
	
	// Fourth group Pth b[3] constant
	and and_gate24 (p[3][0], b[3], a[0]);
	and and_gate25 (p[3][1], b[3], a[1]);
	and and_gate26 (p[3][2], b[3], a[2]);
	and and_gate27 (p[3][3], b[3], a[3]);
	and and_gate28 (p[3][4], b[3], a[4]);
	and and_gate29 (p[3][5], b[3], a[5]);
	and and_gate30 (p[3][6], b[3], a[6]);
	and and_gate31 (p[3][7], b[3], a[7]);

	// Fifth group Pth b[4] constant
	and and_gate32 (p[4][0], b[4], a[0]);
	and and_gate33 (p[4][1], b[4], a[1]);
	and and_gate34 (p[4][2], b[4], a[2]);
	and and_gate35 (p[4][3], b[4], a[3]);
	and and_gate36 (p[4][4], b[4], a[4]);
	and and_gate37 (p[4][5], b[4], a[5]);
	and and_gate38 (p[4][6], b[4], a[6]);
	and and_gate39 (p[4][7], b[4], a[7]);
	
	// Sixth group Pth b[5] constant
	and and_gate40 (p[5][0], b[5], a[0]);
	and and_gate41 (p[5][1], b[5], a[1]);
	and and_gate42 (p[5][2], b[5], a[2]);
	and and_gate43 (p[5][3], b[5], a[3]);
	and and_gate44 (p[5][4], b[5], a[4]);
	and and_gate45 (p[5][5], b[5], a[5]);
	and and_gate46 (p[5][6], b[5], a[6]);
	and and_gate47 (p[5][7], b[5], a[7]);
	
	// Seventh group Pth b[6] constant
	and and_gate48 (p[6][0], b[6], a[0]);
	and and_gate49 (p[6][1], b[6], a[1]);
	and and_gate50 (p[6][2], b[6], a[2]);
	and and_gate51 (p[6][3], b[6], a[3]);
	and and_gate52 (p[6][4], b[6], a[4]);
	and and_gate53 (p[6][5], b[6], a[5]);
	and and_gate54 (p[6][6], b[6], a[6]);
	and and_gate55 (p[6][7], b[6], a[7]);
	
	// Eighth group Pth b[7] constant
	and and_gate56 (p[7][0], b[7], a[0]);
	and and_gate57 (p[7][1], b[7], a[1]);
	and and_gate58 (p[7][2], b[7], a[2]);
	and and_gate59 (p[7][3], b[7], a[3]);
	and and_gate60 (p[7][4], b[7], a[4]);
	and and_gate61 (p[7][5], b[7], a[5]);
	and and_gate62 (p[7][6], b[7], a[6]);
	and and_gate63 (p[7][7], b[7], a[7]);

    wire [5:1]sh,ch;
    wire [6:1]sac,cac;
    wire [3:1]sac2,cac2;
    wire [9:1]sc,cc,cC;
    wire [2:1]sf,cf;

    //Approximate Region
    //Half Adders
    HA HA1(sh[1],ch[1],p[0][4],p[1][3]);
    HA HA2(sh[2],ch[2],p[4][2],p[5][1]);

    ap_comp2 A1comp1(sac[1],cac[1],p[0][5],p[1][4],p[2][3],p[3][2]);
    ap_comp2 A1comp2(sac[2],cac[2],p[0][6],p[1][5],p[2][4],p[3][3]);
    ap_comp2 A1comp3(sac[3],cac[3],p[0][3],p[1][2],p[2][1],p[3][0]);
    ap_comp2 A1comp4(sac[4],cac[4],sh[1],p[2][2],p[3][1],p[4][0]);
    ap_comp2 A1comp5(sac[5],cac[5],sac[1],ch[1],p[4][1],p[5][0]);
    ap_comp2 A1comp6(sac[6],cac[6],sac[2],sh[2],cac[1],p[6][0]);

    ap_comp2 A2comp1(sac2[1],cac2[1],p[0][7],p[1][6],p[2][5],p[3][4]);
    ap_comp2 A2comp2(sac2[2],cac2[2],p[4][3],p[5][2],p[6][1],p[7][0]);
    ap_comp2 A2comp3(sac2[3],cac2[3],sac2[1],sac2[2],cac[2],ch[2]);
    HA HA5(sh[5],ch[5],p[0][2],p[1][1]);

    //Accurate Region
    ex_comp Excomp1(sc[1],cC[1],cc[1],cac2[1],p[1][7],p[2][6],p[3][5],p[4][4]);
    HA HA3(sh[3],ch[3],p[5][3],p[6][2]);
    ex_comp Excomp2(sc[2],cC[2],cc[2],cC[1],p[2][7],p[3][6],p[4][5],p[5][4]);
    HA HA4(sh[4],ch[4],p[6][3],p[7][2]);
    ex_comp Excomp3(sc[3],cC[3],cc[3],cC[2],p[3][7],p[4][6],p[5][5],p[6][4]);
    FA FA1(sf[1],cf[1],cC[3],p[4][7],p[5][6]);


    ex_comp Excomp4(sc[4],cC[4],cc[4],1'b0,sc[1],sh[3],cac2[2],p[7][1]);
    ex_comp Excomp5(sc[5],cC[5],cc[5],cC[4],sc[2],ch[3],cc[1],sh[4]);
    ex_comp Excomp6(sc[6],cC[6],cc[6],cC[5],sc[3],cc[2],ch[4],p[7][3]);
    ex_comp Excomp7(sc[7],cC[7],cc[7],cC[6],sf[1],cc[3],p[6][5],p[7][4]);
    ex_comp Excomp8(sc[8],cC[8],cc[8],cC[7],cf[1],p[5][7],p[6][6],p[7][5]);
    FA FA2(sf[2],cf[2],cC[8],p[6][7],p[7][6]);

	wire [15:0] X,Y;

    assign X = {1'b0,p[7][7],sf[2],sc[8:4],sac2[3],sac[6:3],sh[5],p[0][1],p[0][0]};
    assign Y = {1'b0,cf[2],cc[8:4],cac2[3],cac[6:3],ch[5],p[2][0],p[1][0],1'b0};


    wire carry;
    carry_look_ahead_16bit CLA(X,Y,1'b0,S,carry);

endmodule

// Conventional 4:2 Compressor
module ex_comp(Sum,Carry,Cout,Cin,x4,x3,x2,x1);
input Cin,x4,x3,x2,x1;
output Sum,Carry,Cout;
wire P1;
FA FA1(P1,Cout,x1,x2,x3);
FA FA2(Sum,Carry,P1,Cin,x4);
endmodule

// Half Adder module
module HA(Sum,Carry,X,Y);
input X,Y;
output Sum,Carry;
xor X1(Sum,X,Y);
and A1(Carry,X,Y);
endmodule

// Full Adder module 
module FA(Sum,Carry,X,Y,Z);
input X,Y,Z;
output Sum,Carry;
wire [3:1]P;
HA HA1(P1,P2,X,Y);
HA HA2(Sum,P3,P1,Z);
or O1(Carry,P2,P3);
endmodule


//Approximate Compressor 1
module ap_comp1(S,Carry,A,B,C,D);
output S,Carry;
input A,B,C,D;

wire w1,w2,w3,w4,w5;
wire y0,y1,y2;
or(w1,A,B);
and(w2,A,B);
or(w3,C,D);
and(w4,C,D);

or(y0,w1,w3);
or(y1,w2,w4);
nand(y2,w1,w3);

or(w5,y1,y2);

and(S,y0,w5);
not(Carry,y2);

endmodule

//Approximate Compressor 2
module ap_comp2(S,Carry,A,B,C,D);
output S,Carry;
input A,B,C,D;

wire w1,w2,w3,w4,w5;
wire y0,y1,y2;
or(w1,A,B);
and(w2,A,B);
or(w3,C,D);
and(w4,C,D);

or(y0,w1,w3);
or(y1,w2,w4);
and(y2,w1,w3);

nor(w5,y1,y2);

and(S,y0,w5);
not(Carry,w5);

endmodule

module carry_look_ahead_16bit(a,b, cin, Sum,cout);
input [15:0] a,b;
input cin;
output [15:0] Sum;
output cout;
wire c1,c2,c3;
carry_look_ahead_4bit cla1 (.a(a[3:0]), .b(b[3:0]), .cin(cin), .sum(Sum[3:0]), .cout(c1));
carry_look_ahead_4bit cla2 (.a(a[7:4]), .b(b[7:4]), .cin(c1), .sum(Sum[7:4]), .cout(c2));
carry_look_ahead_4bit cla3 (.a(a[11:8]), .b(b[11:8]), .cin(c2), .sum(Sum[11:8]), .cout(c3));
carry_look_ahead_4bit cla4 (.a(a[15:12]), .b(b[15:12]), .cin(c3), .sum(Sum[15:12]), .cout(cout));

endmodule


module carry_look_ahead_4bit(a,b, cin, sum,cout);
input [3:0] a,b;
input cin;
output [3:0] sum;
output cout;

wire [3:0] p,g,c;

assign p=a^b;//propagate
assign g=a&b; //generate

//carry=gi + Pi.ci

assign c[0]=cin;
assign c[1]= g[0]|(p[0]&c[0]);
assign c[2]= g[1] | (p[1]&g[0]) | p[1]&p[0]&c[0];
assign c[3]= g[2] | (p[2]&g[1]) | p[2]&p[1]&g[0] | p[2]&p[1]&p[0]&c[0];
assign cout= g[3] | (p[3]&g[2]) | p[3]&p[2]&g[1] | p[3]&p[2]&p[1]&g[0] | p[3]&p[2]&p[1]&p[0]&c[0];
assign sum=p^c;

endmodule
