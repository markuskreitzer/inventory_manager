# Function to review the item details and confirm before uploading to Square
def review_and_confirm(name, description, price):
    print("\nPlease review the following information:")
    print(f"Name: {name}")
    print(f"Description: {description}")
    print(f"Price: ${price:.2f}")

    while True:
        choice = input("\nDo you want to post this item? (yes/no/edit): ").lower()
        if choice == 'yes':
            return True, name, description, price
        elif choice == 'no':
            return False, name, description, price
        elif choice == 'edit':
            print("\nEnter new values (or press Enter to keep current value):")
            new_name = input(f"Name [{name}]: ") or name
            new_description = input(f"Description [{description}]: ") or description
            new_price = input(f"Price in dollars [{price}]: ") or price
            return True, new_name, new_description, int(new_price)
        else:
            print("Invalid choice. Please enter 'yes', 'no', or 'edit'.")

