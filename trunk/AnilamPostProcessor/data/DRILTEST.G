G21 (mm units)
G90 (absolute mode)

G0 X10 Y10 Z5.0
G83 Z-10.0 R0.1 Q3.0 F100 (start peck drilling cycle)
X10 Y20
X10 Y30
X20 Y10
X20 Y20
X20 Y30
X30 Y10
X30 Y20
X30 Y30
G80


G0 X40 Y10 Z5.0
G81 Z-10.0 R0.1 F100 (start normal drilling cycle)
X40 Y20
X40 Y30
X50 Y10
X50 Y20
X50 Y30
X60 Y10
X60 Y20
X60 Y30
G80

G0 X0 Y0

M2