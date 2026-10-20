module Reorder_Comp(S,Carry,A,B,C,D);
output S,Carry;
input A,B,C,D;

wire y0,y1,y2;
wire w1,w2,w3,w4,w5,w6;

or(w1,A,B);
and(w2,A,B);
or(w3,C,D);
and(w4,C,D);
or(y0,w1,w3);
and(y1,w1,w3);
or(y2,w2,w4);

or(w5,y2,y1);
not(w6,w5);
and(S,w6,y0);
and(Carry,y0,w5);


endmodule

