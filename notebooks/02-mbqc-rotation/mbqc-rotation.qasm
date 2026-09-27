OPENQASM 3.0;
include "stdgates.inc";

input angle[32] theta;
input angle[32] phi;
input angle[32] xi;
input angle[32] eta;
input angle[32] zeta;

qubit[5] q;

bit[4] bits;

// ============================================================
// MBQC implementation of an arbitrary single-qubit rotation
//
// U_R(xi, eta, zeta) = U_x(zeta) U_z(eta) U_x(xi)
//
// Linear cluster:
// q[0] -- q[1] -- q[2] -- q[3] -- q[4]
//
// Paper numbering:
// q[0], ..., q[4] <-> qubits 1, ..., 5
//
// Input state:
// |psi_in> = Rz(phi) Ry(theta) |0>
//
// Output qubit:
// q[4]
// ============================================================


// ------------------------------------------------------------
// 1. Prepare the arbitrary input state on q[0]
// ------------------------------------------------------------

ry(theta) q[0];
rz(phi) q[0];

barrier q;


// ------------------------------------------------------------
// 2. Prepare q[1], ..., q[4] in |+> and build the chain
//
// All CZ gates commute, so preparing the ancillary chain first
// and then coupling q[0] to q[1] is equivalent to creating the
// complete five-qubit linear cluster in one step.
// ------------------------------------------------------------

h q[1];
h q[2];
h q[3];
h q[4];

cz q[1], q[2];
cz q[2], q[3];
cz q[3], q[4];

cz q[0], q[1];

barrier q;


// ------------------------------------------------------------
// Measurement convention
//
// B(alpha) = {
//   (|0> + exp(i alpha)|1>)/sqrt(2),
//   (|0> - exp(i alpha)|1>)/sqrt(2)
// }
//
// In Qiskit/OpenQASM, a measurement in B(alpha) is implemented
// by Rz(-alpha), then H, then a Z-basis measurement.
// ------------------------------------------------------------


// ------------------------------------------------------------
// 3. Measure paper qubit 1 = q[0]
//
// alpha_1 = 0  ->  X-basis measurement
// ------------------------------------------------------------

h q[0];
bits[0] = measure q[0];


// ------------------------------------------------------------
// 4. Measure paper qubit 2 = q[1]
//
// alpha_2 = -xi * (-1)^bits[0] = (-1)^(bits[0] + 1) xi
//
// If bits[0] = 0: alpha_2 = -xi -> apply Rz(+xi)
// If bits[0] = 1: alpha_2 = +xi -> apply Rz(-xi)
// ------------------------------------------------------------

if (bits[0] == false) {
    rz(xi) q[1];
} else {
    rz(-xi) q[1];
}

h q[1];
bits[1] = measure q[1];


// ------------------------------------------------------------
// 5. Measure paper qubit 3 = q[2]
//
// alpha_3 = -eta * (-1)^bits[1] = (-1)^(bits[1] + 1) eta
//
// If bits[1] = 0: alpha_3 = -eta -> apply Rz(+eta)
// If bits[1] = 1: alpha_3 = +eta -> apply Rz(-eta)
// ------------------------------------------------------------

if (bits[1] == false) {
    rz(eta) q[2];
} else {
    rz(-eta) q[2];
}

h q[2];
bits[2] = measure q[2];


// ------------------------------------------------------------
// 6. Measure paper qubit 4 = q[3]
//
// alpha_4 = -zeta * (-1)^(bits[0] + bits[2])
//         = (-1)^(bits[0] + bits[2] + 1) zeta
//
// If bits[0] XOR bits[2] = 0: alpha_4 = -zeta -> apply Rz(+zeta)
// If bits[0] XOR bits[2] = 1: alpha_4 = +zeta -> apply Rz(-zeta)
// ------------------------------------------------------------

if (bits[0] == false) {

    if (bits[2] == false) {
        // bits[0] XOR bits[2] = 0
        rz(zeta) q[3];
    } else {
        // bits[0] XOR bits[2] = 1
        rz(-zeta) q[3];
    }

} else {

    if (bits[2] == false) {
        // bits[0] XOR bits[2] = 1
        rz(-zeta) q[3];
    } else {
        // bits[0] XOR bits[2] = 0
        rz(zeta) q[3];
    }
}

h q[3];
bits[3] = measure q[3];

barrier q;


// ============================================================
// 7. Remove the Pauli byproduct
//
// Before correction:
//
// |psi_out'> =
// X^(bits[1] XOR bits[3]) Z^(bits[0] XOR bits[2])
// U_R(xi, eta, zeta) |psi_in>
//
// Therefore the inverse correction is
//
// Z^(bits[0] XOR bits[2]) X^(bits[1] XOR bits[3]).
//
// Since gates act on the state from right to left, the QASM
// program applies X first and Z second.
// ============================================================


// ------------------------------------------------------------
// Apply X if bits[1] XOR bits[3] = 1
// ------------------------------------------------------------

if (bits[1] == false) {

    if (bits[3] == true) {
        x q[4];
    }

} else {

    if (bits[3] == false) {
        x q[4];
    }
}


// ------------------------------------------------------------
// Apply Z if bits[0] XOR bits[2] = 1
// ------------------------------------------------------------

if (bits[0] == false) {

    if (bits[2] == true) {
        z q[4];
    }

} else {

    if (bits[2] == false) {
        z q[4];
    }
}


// ============================================================
// q[4] now contains:
//
// U_R(xi, eta, zeta) |psi_in>
// ============================================================
