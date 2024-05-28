import os

from denser_retriever.utils import standardize_normalize, min_max_normalize


def save_data(
    group_data, output_feature, output_group, features, features_to_normalize
):
    if len(group_data) == 0:
        return

    output_group.write(str(len(group_data)) + "\n")
    # collect feature values
    if features_to_normalize:
        features_raw = {f: [] for f in features_to_normalize}
        for data in group_data:
            for p in data[2:]:
                f_name, f_value = p.split(":")
                if f_name in features_to_normalize:
                    features_raw[f_name].append(float(f_value))

        # normalized features_raw
        features_standardize = {}
        features_min_max = {}
        for f in features_to_normalize:
            features_standardize[f] = standardize_normalize(features_raw[f])
            features_min_max[f] = min_max_normalize(features_raw[f])

    for i, data in enumerate(group_data):
        # only include nonzero features
        feats = []

        for p in data[2:]:
            f_name, f_value = p.split(":")
            if features and f_name not in features:
                continue
            if float(f_value) != 0.0:
                feats.append(p)

        if features_to_normalize:
            f_id = len(data[2:]) + 1
            feats_normalized = []
            for j, f in enumerate(features_to_normalize):
                if features_standardize[f][i] != 0.0:
                    feats_normalized.append(
                        f"{f_id + 2 * j}:{features_standardize[f][i]}"
                    )
                if features_min_max[f][i] != 0.0:
                    feats_normalized.append(
                        f"{f_id + 2 * j + 1}:{features_min_max[f][i]}"
                    )
            output_feature.write(
                data[0]
                + " "
                + " ".join(feats)
                + " "
                + " ".join(feats_normalized)
                + "\n"
            )
        else:
            output_feature.write(data[0] + " " + " ".join(feats) + "\n")


def prepare_xgbdata(
    exp_dir, out_file, out_group_file, features_to_use, features_to_normalize
):
    fi = open(os.path.join(exp_dir, "features.svmlight"))
    output_feature = open(os.path.join(exp_dir, out_file), "w")
    output_group = open(os.path.join(exp_dir, out_group_file), "w")
    if features_to_use:
        features_to_use = features_to_use.split(",")
    if features_to_normalize:
        features_to_normalize = features_to_normalize.split(",")

    group_data = []
    group = ""
    for line in fi:
        if not line:
            break
        if "#" in line:
            line = line[: line.index("#")]
        splits = line.strip().split(" ")
        if splits[1] != group:
            # print(f"Processing group {group}")
            save_data(
                group_data,
                output_feature,
                output_group,
                features_to_use,
                features_to_normalize,
            )
            group_data = []
        group = splits[1]
        group_data.append(splits)

    save_data(
        group_data, output_feature, output_group, features_to_use, features_to_normalize
    )

    fi.close()
    output_feature.close()
    output_group.close()


def merge_files(input_dirs, file_names, output_dir):
    """
    Merges files with the same name across multiple directories and saves the merged file to the output directory.

    :param input_dirs: List of input directories.
    :param file_names: List of file names to merge.
    :param output_dir: Output directory where merged files will be saved.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_name in file_names:
        merged_content = []

        for input_dir in input_dirs:
            file_path = os.path.join(input_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    merged_content.append(file.read())

        output_file_path = os.path.join(output_dir, file_name)
        with open(output_file_path, "w") as output_file:
            output_file.write("".join(merged_content))


if __name__ == "__main__":
    dataset_names = [
        "exp_cqadupstack-android",
        "exp_cqadupstack-english",
        "exp_cqadupstack-gaming",
        "exp_cqadupstack-gis",
        "exp_cqadupstack-mathematica",
        "exp_cqadupstack-physics",
        "exp_cqadupstack-programmers",
        "exp_cqadupstack-stats",
        "exp_cqadupstack-tex",
        "exp_cqadupstack-unix",
        "exp_cqadupstack-webmasters",
        "exp_cqadupstack-wordpress",
    ]

    input_dirs = [
        f"/home/ubuntu/denser_output_retriever/{name}/test" for name in dataset_names
    ]
    file_names = [
        "qrels.jsonl",
        "features.svmlight",
        "es+vs",
        "es+rr",
        "vs+rr",
        "es+vs+rr",
        "es+vs_n",
        "es+rr_n",
        "vs+rr_n",
        "es+vs+rr_n",
        "es+vs.group",
        "es+rr.group",
        "vs+rr.group",
        "es+vs+rr.group",
        "es+vs_n.group",
        "es+rr_n.group",
        "vs+rr_n.group",
        "es+vs+rr_n.group",
    ]
    output_dir = "/home/ubuntu/denser_output_retriever/exp_cqadupstack-all/test"
    merge_files(input_dirs, file_names, output_dir)
