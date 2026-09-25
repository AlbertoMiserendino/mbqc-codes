OPENQASM 3.0;

include "stdgates.inc";

qubit[4] q;
bit[4] c;

// Parameters of the state to prepare
input angle theta;
input angle phi;


// Prepare the state |psi> on q0
ry(theta) q[0];
rz(phi) q[0];

// Prepare the ancillas in |+>
h q[1];
h q[2];
h q[3];

barrier q;

// Linear cluster
ctrl @ z q[1], q[2];
ctrl @ z q[2], q[3];

// Entangling
ctrl @ z q[0], q[1];

barrier q;

// Measure q0,q1,... in the X basis

h q[0];
h q[1];
h q[2];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];

barrier q;

// --------------------------------
// Feed-forward
// --------------------------------

// X^(m0 XOR m2)

if (c[0] == true) {
    x q[3];
}

if (c[2] == true) {
    x q[3];
}

// Z^m1

if (c[1] == true) {
    z q[3];
}

// Remove the residual H
// Each X measurement introduces an H.
// If the number of teleportation steps is odd:
h q[3];

// Final verification is not included
