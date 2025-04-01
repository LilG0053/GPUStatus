import bcolors as colors

class ph:
    def printNotAvailable(self, product_name):
        c = colors.bcolors()
        print(f"{c.FAIL}Product is not available: {c.ENDC} {product_name} ")
    def printMessageSent(self):
        print(f"{colors.OKCYAN}Message sent to phone{colors.ENDC}")