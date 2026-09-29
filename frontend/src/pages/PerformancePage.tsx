import { Fragment } from 'react';
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { vitMetrics } from '../data/metrics';

export default function PerformancePage() {
    const chartData = vitMetrics.classes.map((row) => ({
        name: row.name,
        Precision: +(row.precision * 100).toFixed(2),
        Recall: +(row.recall * 100).toFixed(2),
        F1: +(row.f1 * 100).toFixed(2),
    }));

    return (
        <div className="min-h-screen px-4 py-10 text-white">
            <div className="mx-auto max-w-6xl">
                <p className="text-xs tracking-[0.28em] text-cyan-300">DEEPWAY // MODEL INTELLIGENCE</p>
                <h1 className="mt-2 text-4xl font-bold">ViT image detector</h1>
                <p className="mt-3 max-w-3xl text-sm text-slate-400">
                    Held-out test set of {vitMetrics.testSamples.toLocaleString()} images.
                    Overall accuracy {(vitMetrics.accuracy * 100).toFixed(2)}%, weighted F1 {vitMetrics.weightedF1.toFixed(3)}.
                    Twelve errors total.
                </p>

                <div className="mt-8 grid gap-4 md:grid-cols-3">
                    {vitMetrics.classes.map((row) => (
                        <div key={row.name} className="hud-frame p-4">
                            <div className="text-xs tracking-widest text-cyan-300">{row.name}</div>
                            <div className="mt-2 text-3xl text-[var(--color-success)]">{(row.auc * 100).toFixed(2)} AUC</div>
                            <div className="mt-2 text-xs text-slate-400">support {row.support}</div>
                        </div>
                    ))}
                </div>

                <div className="hud-frame mt-6 p-4">
                    <h2 className="mb-4 text-lg">Precision, recall, F1</h2>
                    <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData}>
                                <CartesianGrid stroke="rgba(0,240,255,0.12)" />
                                <XAxis dataKey="name" stroke="#94a3b8" />
                                <YAxis domain={[98, 100]} stroke="#94a3b8" />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="Precision" fill="#00f0ff" />
                                <Bar dataKey="Recall" fill="#39ff14" />
                                <Bar dataKey="F1" fill="#ff2bd6" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="mt-6 grid gap-4 md:grid-cols-2">
                    <div className="hud-frame p-4">
                        <h2 className="mb-4 text-lg">Confusion matrix</h2>
                        <div className="confusion">
                            <div />
                            {vitMetrics.confusion.labels.map((label) => <div key={label}>{label}</div>)}
                            {vitMetrics.confusion.matrix.map((row, i) => (
                                <Fragment key={vitMetrics.confusion.labels[i]}>
                                    <div>{vitMetrics.confusion.labels[i]}</div>
                                    {row.map((value, j) => (
                                        <div key={`${i}-${j}`} className={i === j ? 'hit' : ''}>{value}</div>
                                    ))}
                                </Fragment>
                            ))}
                        </div>
                    </div>
                    <div className="hud-frame p-4 text-sm leading-7 text-slate-300">
                        <h2 className="mb-2 text-lg text-white">Training</h2>
                        <div>Learning rate {vitMetrics.training.learningRate}</div>
                        <div>Batch size {vitMetrics.training.batchSize}</div>
                        <div>Epochs {vitMetrics.training.epochs}</div>
                        <div>Weight decay {vitMetrics.training.weightDecay}</div>
                        <div>Label smoothing {vitMetrics.training.labelSmoothing}</div>
                        <p className="mt-4 text-xs text-slate-500">
                            Base checkpoint {vitMetrics.checkpoint}. The hardest boundary is Real versus Deepfake: 6 real images were called deepfake.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
