PRAGMA foreign_keys = ON;

INSERT INTO data(totalCarbonEmission, solarCarbonEmission, evCarbonEmission, emsCarbonEmission, netInvertertoGrid, netSolartoInverter, netInvertertoComps)
VALUES
    (4268, 2838, 835, 565, -0.2, 0.23, 0.43);


INSERT INTO chart(baselineEmission, noEMSEmission, withEMSEmission)
VALUES
    (600, 432, 118),
    (550, 375, 175),
    (650, 400, 150),
    (500, 350, 150),
    (600, 380, 120),
    (566, 394, 227),
    (564, 322, 145),
    (592, 367, 183),
    (566, 473, 200),
    (595, 350, 185),
    (572, 345, 168),
    (578, 360, 178),
    (555, 340, 185),
    (590, 355, 175),
    (565, 330, 155),
    (575, 340, 195),
    (585, 355, 170),
    (550, 335, 175),
    (592, 340, 180);
