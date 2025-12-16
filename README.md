# FPGA-Accelerated FIR Filters on PYNQ-Z2

## Project Overview
This project presents a high-performance, hardware-accelerated digital audio filters implemented on the PYNQ-Z2 FPGA board using the Xilinx Zynq-7000 SoC. The system is designed to offload computationally intensive Digital Signal Processing (DSP) tasks—specifically Finite Impulse Response (FIR) filtering—from the general-purpose processor to the Programmable Logic (PL). By utilizing custom hardware overlays, the design demonstrates significant efficiency improvements and architectural flexibility compared to purely software-based signal processing solutions.

## System Architecture
The project employs a Hardware-Software Co-Design methodology, illustrated in the Vivado Block Design below:


* **Programmable Logic (Hardware):** The signal processing pipeline is constructed using the Xilinx FIR Compiler IP core, integrated with an AXI Direct Memory Access (DMA) engine. This configuration enables high-bandwidth audio data streaming directly between the system memory (DDR) and the FPGA fabric.
* **Processing System (Software):** A Python-based control layer running on the embedded Linux OS (via Jupyter Notebooks) manages the data flow, handles audio file I/O, and interfaces with the hardware drivers.

## Key Features

* **FPGA-Based Signal Processing:** Implements precise digital filtering (Low Pass, Band Pass, and High Pass) on the hardware fabric, utilizing DSP slices for parallelized arithmetic operations.
* **Dynamic Hardware Reconfiguration:** Features the ability to swap hardware bitstreams at runtime, allowing the system to switch between different filter characteristics instantly without a system reboot.
* **High-Speed Data Transport:** Utilizes the AXI4-Stream protocol and AXI DMA to maximize data throughput and minimize CPU intervention during audio processing.
* **Interactive Analysis Interface:** Includes a custom Graphical User Interface (GUI) that allows users to load audio files, apply hardware filters, and perform time-domain analysis through waveform visualization.
* **Custom Filter Design:** Utilizes 81-tap coefficients generated via the Kaiser window method to ensure optimal frequency response and stability.

## License
This project is licensed under the MIT License.

