from mcodingbot.utils import Plugin
# import crescent
import crescent
# import abstract classes
import abc

# Create the `crescent` plugin object
plugin = Plugin()


# Create the exception for when a joke is not found
class JokeNotFoundError(Exception):
    ...


# Define the abstract joke
class AbstractJoke(abc.ABC):
    # Define the get joke abstract method
    @abc.abstractmethod
    def get_joke(self) -> str:
        ...

    # Define the get author abstract method
    @abc.abstractmethod
    def get_author(self) -> str:
        ...

    # Define the `toString` method
    def __str__(self) -> str:
        return f"{self.get_joke()}\n" f"Written by {self.get_author()}"


# Define an abstract one liner class that extends from the abstract joke
class AbstractOneLiner(AbstractJoke):
    # Define the get punchline method
    @abc.abstractmethod
    def get_punchline(self) -> str:
        ...

    # Override the `toString` method
    def __str__(self) -> str:
        # Return the String
        return f"{self.get_joke()}\n\n" f"A: ||{self.get_punchline()}||"


# Define the `PoleJoke`
class PoleJoke(AbstractOneLiner):
    # Implement the get joke method
    def get_joke(self) -> str:
        # Return the String
        return "What is the value of a contour integral around western europe?"

    # Implement the get author method
    def get_author(self) -> str:
        # Return the String
        return "mCoding"

    # Implement the get punchline method
    def get_punchline(self) -> str:
        # Return the String
        return "zero, all the poles are in eastern europle."


# Define the joke factory
class JokeFactory:
    def get_joke(self, joke: str) -> AbstractJoke:
        # Check the type of the joke
        if joke == "PoleJoke":
            # return the PoleJoke
            return PoleJoke()
        # Raise an exception when the joke is not found
        raise JokeNotFoundError()


# Add the command to the plugin class
@plugin.include
# Create a command with the name joke
@crescent.command(name="joke")
class Joke:
    # respond to the command
    async def callback(self, ctx: crescent.Context) -> None:
        # Create the joke factory
        joke_factory = JokeFactory()
        # get the joke from the JokeFactory
        joke = joke_factory.get_joke("PoleJoke")
        # Respond with the joke
        await self.respond_with_joke(ctx, joke)

    # Create a function to respond to the command with the joke
    async def respond_with_joke(self, ctx: crescent.Context, joke: AbstractJoke) -> None:
        # respond to the command with the joke
        await ctx.respond(str(joke))
