PRAGMA foreign_keys = ON;

INSERT INTO data(totalCarbonEmission, solarCarbonEmission, evCarbonEmission, emsCarbonEmission, netInvertertoGrid, netSolartoInverter, netInvertertoComps)
VALUES
    (4268, 2838, 835, 565, -0.2, 0.23, 0.43);


INSERT INTO chart(baselineEmission, noEMSEmission, withEMSEmission)
VALUES
    (245, 134, 120),
    (356, 245, 124),
    (467, 345, 267);
