from faker import Faker
import sys
import os


def main(seed):
    f = Faker()
    f.seed(seed)
    num = [10, 100, 1000, 10000, 100000, 1000000]
    providers = [f.file_path, f.ipv4, f.phone_number]
    # generate fake files

    if not os.path.exists("collision_results.csv"):
        with open("collision_results.csv", 'w') as f:
            f.write("seed, provider, total, unique, pct_unique\n")

    with open("collision_results.csv", "a") as f:
        for provider in providers:
            print("working on: {}".format(provider.__name__))
            for n in num:
                files = []
                for i in range(n):
                    files.append(provider())

                f.write("{},{},{},{},{: .4f}\n".format(
                    seed,
                    provider.__name__,
                    n,
                    len(list(set(files))),
                    100*((len(list(set(files))))/n))
                )


if __name__ == "__main__":
    seed = sys.argv[1]
    main(seed)
