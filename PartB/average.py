def Main():
        numbers_input = [5, 8, 12, 4, 10]
        total = 0
        for number in numbers_input:
            total += number
        average = total / len(numbers_input)
        print(f"The average of the numbers is {average}")


if __name__ == "__main__":
    Main()