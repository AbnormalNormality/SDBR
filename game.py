from copy import deepcopy
from inspect import currentframe
from random import shuffle
from typing import Any, Callable


class Class:
    def __repr__(self) -> str:
        return f"{type(self).__name__}({", ".join([f"{k}: {repr(v)}" for k, v in self.__dict__.items()])})"

    def copy(self):
        return deepcopy(self)


def gen_context(back: int = 1) -> dict[str, Any]:
    frame = currentframe()

    for _ in range(back):
        frame = frame.f_back

    return frame.f_locals


class TriggerConstant(Class):
    FORCE = 'trigger.force'


TC = TriggerConstant

# Bare bones


class Base(Class):
    def __init__(self, name: str):
        self.name: str = name


class Entity(Class):
    def __init__(self, name: str, max_hp: int):
        self.isPlayer: bool = False
        self.name: str = name

        self.maxHp: int = max_hp
        self.hp: int = self.maxHp


class Trigger(Class):
    def __init__(self, trigger: str, function: Callable[[dict], None]):
        if function is None: function = lambda d: None

        self.trigger: str = trigger
        self.function: Callable[[dict], None] = function

    def __call__(self, context: dict): self.function(context)


# Skin


class Card(Base):
    def __init__(self, name: str, triggers: list[Trigger] = None):
        if triggers is None: triggers = []

        super().__init__(name)

        self.triggers: list[Trigger] = triggers


class Player(Entity):
    def __init__(self, name: str, max_hp: int):
        super().__init__(name, max_hp)

        self.deck: list[Card] = []
        self.hand: list[Card] = []
        self.discardPile: list[Card] = []

        self.isPlayer = True

        self.handSize: int = 4

    # noinspection PyUnusedLocal
    def play_card(self, index_in_hand: int, targets: list[Entity]):
        card = self.hand[index_in_hand]

        for t in card.triggers:
            if t.trigger == TC.FORCE:
                t(gen_context())

    def draw(self, n: int):
        for _ in range(n):
            if len(self.deck) == 0:
                discard_pile = self.discardPile.copy()
                self.discardPile.clear()
                self.deck.extend(discard_pile)
                shuffle(self.deck)

            if len(self.deck) == 0: break

            card: Card = self.deck.pop(0)
            self.hand.append(card)

    def start_turn(self):
        self.draw(self.handSize)

    def end_turn(self):
        hand = self.hand.copy()
        self.hand.clear()
        self.discardPile.extend(hand)


#


def main():
    from os import system

    player = Player("Alia", 80)

    damage_card = Card("Damage", [Trigger(TC.FORCE, lambda _: print("I'M GOING TO BEAT YOU TO DEATH!!!"))])
    shield_card = Card("Shield",
                       [Trigger(TC.FORCE, lambda _: print("Plz dont hurt me :("))])
    special_card = Card("Special", [Trigger(TC.FORCE, lambda _: print("My sister calls me special :3"))])

    player.discardPile.extend([
        damage_card.copy(),
        damage_card.copy(),
        damage_card.copy(),
        damage_card.copy(),
        shield_card.copy(),
        shield_card.copy(),
        shield_card.copy(),
        special_card.copy(),
    ])

    enemy = Entity("Enemy 1", 40)
    enemies = [enemy]

    while True:
        player.start_turn()

        print(f"{player.name} ({player.hp}/{player.maxHp})")

        print("\n", end="")

        for i, c in enumerate(player.hand):
            print(f"({i}) {c.name}")

        card_index = input("What card do you want to play?\n")

        while not card_index.isdigit() or len(player.hand) < int(card_index) < 0:
            card_index = input(f"Please choose a number between 0 and {len(player.hand) - 1}.\n")

        print("\n", end="")

        for i, e in enumerate(enemies):
            print(f"({i}) {e.name} ({e.hp}/{e.maxHp})")

        target_index = input("Who do you want to target?\n")

        while not target_index.isdigit() or len(enemies) < int(target_index) < 0:
            target_index = input(f"Please choose a number between 0 and {len(enemies) - 1}.\n")

        card = int(card_index)
        targets = [enemies[int(target_index)]]

        system("cls||clear")

        print(f"You play '{player.hand[card].name}' against {", ".join([f"'{e.name}'" for e in targets])}")
        player.play_card(card, targets)

        print("\n", end="")

        player.end_turn()


__all__ = []

if __name__ == '__main__': main()
