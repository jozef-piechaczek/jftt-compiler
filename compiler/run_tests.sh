#!/bin/bash
RESULTS='../tests/results/'
VM='../vm/maszyna-wirtualna'
CYAN='\033[0;36m'
NC='\033[0m'
${VM} ${RESULTS}'00-div-mod.imp.mr' <<< "33 7"
echo -e "${CYAN}end of 00${NC}"
${VM} ${RESULTS}'0-div-mod.imp.mr' <<< "1 0"
echo -e "${CYAN}end of 0${NC}"
${VM} ${RESULTS}'1-numbers.imp.mr' <<< "10"
echo -e "${CYAN}end of 1${NC}"
${VM} ${RESULTS}'2-fib.imp.mr' <<< "1"
echo -e "${CYAN}end of 2${NC}"
${VM} ${RESULTS}'3-fib-factorial.imp.mr' <<< "20"
echo -e "${CYAN}end of 3${NC}"
${VM} ${RESULTS}'4-factorial.imp.mr' <<< "20"
echo -e "${CYAN}end of 4${NC}"
${VM} ${RESULTS}'5-tab.imp.mr'
echo -e "${CYAN}end of 5${NC}"
${VM} ${RESULTS}'6-mod-mult.imp.mr' <<< "1234567890 1234567890987654321 987654321"
echo -e "${CYAN}end of 6${NC}"
${VM} ${RESULTS}'7-loopiii.imp.mr' <<< "0 0 0"
echo -e "${CYAN}end of 7${NC}"
${VM} ${RESULTS}'7-loopiii.imp.mr' <<< "1 0 2"
echo -e "${CYAN}end of 7${NC}"
${VM} ${RESULTS}'8-for.imp.mr' <<< "12 23 34"
echo -e "${CYAN}end of 8${NC}"
${VM} ${RESULTS}'9-sort.imp.mr'
echo -e "${CYAN}end of 9${NC}"
${VM} ${RESULTS}'program0.imp.mr' <<< "127"
echo -e "${CYAN}end of p0${NC}"
${VM} ${RESULTS}'program1.imp.mr'
echo -e "${CYAN}end of p1${NC}"
${VM} ${RESULTS}'program2.imp.mr' <<< "36"
echo -e "${CYAN}end of p2${NC}"