/** Held-out test metrics for the ViT image detector. Numbers only, no sample images. */
export const vitMetrics = {
    model: "ViT-Base/16",
    checkpoint: "google/vit-base-patch16-224-in21k",
    testSamples: 2000,
    accuracy: 0.994,
    weightedF1: 0.994,
    classes: [
        { name: "Artificial", accuracy: 0.9985, precision: 0.9926, recall: 0.9985, f1: 0.9955, support: 672, auc: 0.9998 },
        { name: "Deepfake", accuracy: 0.9926, precision: 0.9896, recall: 0.9926, f1: 0.9911, support: 674, auc: 0.9997 },
        { name: "Real", accuracy: 0.9908, precision: 1, recall: 0.9908, f1: 0.9954, support: 654, auc: 0.9999 },
    ],
    confusion: {
        labels: ["Artificial", "Deepfake", "Real"],
        matrix: [
            [671, 1, 0],
            [5, 669, 0],
            [0, 6, 648],
        ],
    },
    training: {
        learningRate: "1e-5",
        batchSize: 16,
        epochs: 5,
        weightDecay: 0.1,
        labelSmoothing: 0.1,
    },
};
