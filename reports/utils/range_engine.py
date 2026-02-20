def check_ranges(values):
    """
    Compares extracted values against standard reference ranges.
    Auto-detects units: if WBC/Platelets are in full counts (>1000), 
    converts to K/uL before checking.
    Returns: {'test': 'Low'|'Normal'|'High'}
    """
    # Ranges in standard K/uL for cell counts, or native units for others
    ranges = {
        "hemoglobin":   (12.0, 17.5),   # g/dL
        "glucose":      (70,   100),     # mg/dL (fasting)
        "rbc":          (4.0,  5.9),     # M/uL
        "wbc":          (4.5,  11.0),    # K/uL
        "platelets":    (150,  450),     # K/uL
        "cholesterol":  (0,    200),     # mg/dL
        "creatinine":   (0.6,  1.3),     # mg/dL
        "ast":          (10,   40),      # U/L
        "alt":          (7,    56),      # U/L
        "neutrophils":  (40,   75),      # %
        "lymphocytes":  (20,   45),      # %
        "monocytes":    (2,    10),      # %
        "eosinophils":  (1,    6),       # %
        "basophils":    (0,    1),       # %
        "pcv":          (36,   50),      # %
        "mcv":          (80,   100),     # fL
        "mch":          (27,   33),      # pg
        "mchc":         (32,   36),      # g/dL
        "hba1c":        (4.0,  5.6),     # %
        "bilirubin":    (0.2,  1.2),     # mg/dL
        "urea":         (7,    20),      # mg/dL
    }

    # Tests that are reported in K/uL but sometimes written as full counts
    cell_count_tests = {"wbc", "platelets"}

    statuses = {}

    for test, value in values.items():
        check_value = value

        # Auto-convert: if it's a cell count test and value > 1000, it's in cells/uL
        if test in cell_count_tests and value > 1000:
            check_value = value / 1000.0  # Convert to K/uL

        if test in ranges:
            low, high = ranges[test]
            if check_value < low:
                statuses[test] = "Low"
            elif check_value > high:
                statuses[test] = "High"
            else:
                statuses[test] = "Normal"
        else:
            statuses[test] = "Unknown"

    return statuses
