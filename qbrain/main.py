import random
import os
from environment import GridWorldEnvironment
from meta import MetaBrain
from brain import QBrain
from memory import MemoryBank
from reflection import ReflectionEngine
from world_memory import WorldMemory


EPISODES_PER_BATCH = 5
MAX_STEPS = 200
WORLD_TYPES = ["corridor", "maze", "trap", "open"]


def run_episode(env, brain, training=True):
    state = env.reset()
    path = [state]

    optimal = None
    if hasattr(env, "shortest_path_length"):
        optimal = env.shortest_path_length()

    env.has_solution = optimal is not None

    for step in range(MAX_STEPS):
        action = brain.choose_action(state, training=training)
        next_state, reward, done = env.step(action)

        if training:
            brain.learn(state, action, reward, next_state)

        state = next_state
        path.append(state)

        if done:
            return step + 1, optimal, path

    return MAX_STEPS, optimal, path


def efficiency(steps, optimal):
    if optimal is None or optimal == 0:
        return 0.0
    return min(1.0, optimal / steps)


def choose_next_world(current_type, world_memory, last_decision):
    if last_decision == "IMPOSSIBLE":
        world_memory.mark_failed(current_type)
    
    candidates = [w for w in WORLD_TYPES if world_memory.is_allowed(w)]
    
    if not candidates:
        candidates = WORLD_TYPES
    
    return random.choice(candidates)


def main():
    print("🧠 Starting optimized agent")

    meta = MetaBrain()
    meta.load()
    
    memory = MemoryBank()
    reflection = ReflectionEngine(threshold=5)
    world_memory = WorldMemory()

    env = GridWorldEnvironment()
    brain = QBrain(env)
    brain.meta = meta

    brain.load()
    meta.load()
    print("🧠 Brain & Meta loaded")

    total_episodes = 0

    try:
        while True:
            print(f"\n{'='*50}")
            print(f"🌍 WORLD: {env.world_type} | Episodes: {total_episodes}")

            batch_eff = []

            for ep in range(EPISODES_PER_BATCH):
                steps, optimal, path = run_episode(env, brain, training=True)
                eff = efficiency(steps, optimal)
                batch_eff.append(eff)
                
                memory.store(env, steps, path, optimal)

                total_episodes += 1

                print(f"  Episode {ep}: {steps} steps | optimal {optimal} | eff {eff:.2f}")

            avg_eff = sum(batch_eff) / len(batch_eff)
            
            for eff in batch_eff:
                meta.record(eff, env.world_type)

            stats = meta.stats()
            print(f"📊 Meta: mean={stats['mean']:.2f} trend={stats['trend']:.2f} ema={stats['ema']:.2f}")

            world_has_solution = env.has_solution
            decision = meta.decide(world_has_solution, env.world_type)
            
            brain_stats = brain.get_stats()
            print(f"🧠 Brain: ε={brain_stats['epsilon']:.3f} Q-size={brain_stats['q_size']} replay={brain_stats['replay_size']}")

            print(f"🧭 Decision: {decision}")

            if decision == "SOLVED":
                print("✅ Agent mastered this world!")
                world_memory.mark_solved(env.world_type, avg_eff)
                
                brain.bias_towards(path)
                
                next_type = "harder" if hasattr(env, "harder") else random.choice(["maze", "trap"])
                env = GridWorldEnvironment(next_type)
                brain.env = env

            elif decision == "IMPOSSIBLE":
                print("❌ World is impossible - abandoning")
                
                brain.penalize(path)
                
                next_type = choose_next_world(env.world_type, world_memory, decision)
                env = GridWorldEnvironment(next_type)
                brain.env = env

            elif decision == "CHANGE_WORLD":
                print("🔄 Agent stuck - switching world")
                
                reflected = reflection.reflect(brain, memory, env)
                if reflected:
                    print("   💭 Reflection applied")
                
                next_type = choose_next_world(env.world_type, world_memory, decision)
                env = GridWorldEnvironment(next_type)
                brain.env = env

            elif decision == "ADAPT_STRATEGY":
                print("🔧 Adapting strategy")
                
                brain.epsilon = min(1.0, brain.epsilon + 0.2)
                reflected = reflection.reflect(brain, memory, env)

            elif decision == "INCREASE_DIFFICULTY":
                print("⬆️ Increasing difficulty")
                
                if hasattr(env, "size"):
                    env = GridWorldEnvironment(env.world_type, size=env.size + 2)
                else:
                    env = GridWorldEnvironment("maze", size=9)
                brain.env = env

            else:
                print("➡️  Continuing in same world")

            if total_episodes % 10 == 0:
                brain.save()
                meta.save()
                memory.save()
                
                insight = reflection.get_insight(memory, env)
                print(f"💡 Insight: {insight}")

    except KeyboardInterrupt:
        print("\n💾 Saving and exiting...")
        brain.save()
        meta.save()
        memory.save()


if __name__ == "__main__":
    main()
