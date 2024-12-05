import pygame

# Backgrounds
road = pygame.image.load("pictures/road.png")
road = pygame.transform.scale(road, (400, 800))
grass = pygame.image.load("pictures/grass.jpg")
grass = pygame.transform.scale(grass, (275, 800))

# Player sprite
bike = pygame.image.load("pictures/bike1.png")
bike = pygame.transform.scale(bike, (70, 140))

# Obstacles sprites
rabbit = pygame.image.load("pictures/rabbit.png")
rabbit = pygame.transform.scale(rabbit, (51, 102))
car1 = pygame.image.load("pictures/car1.png")
car1 = pygame.transform.scale(car1, (120, 240))
car2 = pygame.image.load("pictures/car2.png")
car2 = pygame.transform.scale(car2, (120, 240))
car3 = pygame.image.load("pictures/car3.png")
car3 = pygame.transform.scale(car3, (120, 240))
car4 = pygame.image.load("pictures/car4.png")
car4 = pygame.transform.scale(car4, (120, 240))
car5 = pygame.image.load("pictures/car5.png")
car5 = pygame.transform.scale(car5, (120, 240))
car6 = pygame.image.load("pictures/car6.png")
car6 = pygame.transform.scale(car6, (120, 240))
car7 = pygame.image.load("pictures/car7.png")
car7 = pygame.transform.scale(car7, (120, 240))
truck = pygame.image.load("pictures/truck.png")
truck = pygame.transform.scale(truck, (120, 240))
tree = pygame.image.load("pictures/tree.png")
tree = pygame.transform.scale(tree, (204, 408))
tree1 = pygame.image.load("pictures/tree1.png")
tree1 = pygame.transform.scale(tree1, (204, 408))
tree2 = pygame.image.load("pictures/tree2.png")
tree2 = pygame.transform.scale(tree2, (204, 408))

# New rectangle asset
rectangle = pygame.Surface((50, 75))  # Create a new surface for the rectangle
rectangle.fill((0, 0, 255))  # Fill it with blue color (RGB: 0, 0, 255)

# Other images
bgimage = pygame.image.load("pictures/Background1.jpg")
roadrage = pygame.image.load("pictures/roadrage.png")
roadrage = pygame.transform.scale(roadrage, (800, 300))
