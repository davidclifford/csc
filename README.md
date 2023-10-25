# CSC
Clifford Small Computer - 25/10/2023

Based on the CSCvon8 by Warren Toomey

### Motivation
After using the CSCvon8 for a few years, hacking it for my own purposes by adding extra commands, changing the ALU and adding VGA and SSD,
I felt it is time to extend the basic design to make it more capable and easier to use but not add too much to the basic design, still keeping it as minimal as possible.

### Proposed Changes
* Adding 2 more general purpose registers C & D to make arithmetic and logic easier and more efficient.
* Getting rid of the Jump logic as this was inflexible and made 16 bit calulations and branching hard, instead having a flags register that feeds into the control ROMS. This also frees up 3 control lines.
* Integrating a Bank register for more memory footprint.
* Making the hacked signals more accessable with a new motherboard.
* Easier expansion, e.g. VGA, SDD and maybe Sound.

