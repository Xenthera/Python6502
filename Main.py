import pygame

import CPU
from CPU import *

class Game:
    def __init__(self):
        self.memory = None
        self.cpu = None
        self.c = None

        pygame.init()

        pygame.display.set_caption('6502 Emulator')
        self.screen = pygame.display.set_mode((1280, 768))

        self.background = pygame.Surface((800, 600))
        self.background.fill(pygame.Color('#000000'))

        self.is_running = True

        self.tex_wid = 256
        self.tex_height = 256
        self.memory_texture = pygame.Surface((self.tex_wid, self.tex_height))
        self.memory_texture_scale = 3

        self.font = pygame.font.Font("Resources/SpaceMono-Regular.ttf", 30)
        self.text_color_normal = (255, 255, 255)

        self.cpu_attributes = ["A", "X", "Y", "PC", "SP", "C", "Z", "I", "D", "B", "V", "N", "address"]

        self.init_cpu()

    def init_cpu(self):
        self.memory = Memory()
        self.cpu = Cpu6502()
        self.cpu.reset(self.memory)
        self.memory[0xFFFC] = INS_JSR
        self.memory[0xFFFD] = 0x42
        self.memory[0xFFFE] = 0x42
        self.memory[0x4242] = INS_JSR
        self.memory[0x4243] = 0x69
        self.memory[0x4244] = 0x69
        self.memory[0x6969] = INS_JSR
        self.memory[0x696A] = 0x42
        self.memory[0x696B] = 0x42
        self.c = CycleCounter(18)

    def start(self):
        while self.is_running:
            self.update()
            pygame.display.update()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.c.cycleCount > 0:
                        self.cpu.tick(self.c, self.memory)

                    else:
                        print("No more cycles")

    def update(self):

        self.handle_input()

        if self.c.cycleCount > 0:
            for i in range(1):
                self.cpu.tick(self.c, self.memory)

        self.screen.fill((50, 150, 120))

        # Draw memory region texture
        for y in range(self.tex_height):
            for x in range(self.tex_wid):
                index = y * self.tex_wid + x
                value = self.memory[index]
                self.memory_texture.set_at((x, y), (value, value, value))


        scaled_texture = pygame.transform.scale(self.memory_texture, (self.memory_texture.get_width() * self.memory_texture_scale, self.memory_texture.get_height() * self.memory_texture_scale))
        self.screen.blit(scaled_texture, (0,0))

        # Draw stack pointer and PC

        x = self.cpu.PC % self.tex_wid
        y = self.cpu.PC // self.tex_wid
        x *= self.memory_texture_scale
        y *= self.memory_texture_scale

        pygame.draw.rect(self.screen, (255, 255, 0), (x - 2, y - 2, 7, 7), width=2)

        x = self.cpu.SP % self.tex_wid
        y = self.cpu.SP // self.tex_wid
        x *= self.memory_texture_scale
        y *= self.memory_texture_scale

        pygame.draw.rect(self.screen, (0, 255, 0), (x - 2, y - 2, 7, 7), width=2)

        pad = 5
        # Draw CPU Vars
        cpu_attribute_values = [getattr(self.cpu, name) for name in self.cpu_attributes]
        attr_count = 0
        for i in range(len(self.cpu_attributes)):
            self.draw_text(self.cpu_attributes[i] + ": " + str(hex(cpu_attribute_values[i])), 256 * self.memory_texture_scale + pad, pad + (self.font.get_height()) * i)
            attr_count = i

        attr_count += 1
        mnemonic = "?"

        if self.memory[self.cpu.PC] in asm_mnemonic:
            mnemonic = asm_mnemonic[self.memory[self.cpu.PC]]


        self.draw_text("Value at PC: " + str(hex(self.memory[self.cpu.PC])) + " : " + mnemonic, 256 * self.memory_texture_scale + pad,
                       pad + (self.font.get_height()) * attr_count)

        attr_count += 1
        self.draw_text("Value at SP: " + str(hex(self.memory[self.cpu.SP])), 256 * self.memory_texture_scale + pad,
                       pad + (self.font.get_height()) * attr_count)

    def draw_text(self, text, x, y):
        rendered_text = self.font.render(text, True, self.text_color_normal)
        self.screen.blit(rendered_text, (x, y))


if __name__ == "__main__":
    game = Game()
    game.start()