import crescent

plugin = crescent.Plugin("basic")


@plugin.include
@crescent.command(name="ping", description="Pong!")
class PingCommand:
    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(f"Pong! {round(ctx.app.heartbeat_latency*1000)} ms.")
