def correct_positions(positions, max_values):
    for i in range(len(positions)):
        for j in range(len(positions[i])):
            if positions[i][j] > max_values[j]:
                positions[i][j] = max_values[j]
    return positions

# Example usage:
positions = [
    [8, 2, 5],
    [6, 4, 12],
    [3, 1, 9]
]

max_values = [7, 3, 10]
corrected_positions = correct_positions(positions, max_values)
print(corrected_positions)
