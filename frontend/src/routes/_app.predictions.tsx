import { createFileRoute } from "@tanstack/react-router";
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { useState } from "react";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/PageHeader";
import { platformApi } from "@/api/platform";

export const Route = createFileRoute("/_app/predictions")({
  component: PredictionsPage,
});

type Customer = {
  id: string;
  name?: string;
  email?: string;
  phone?: string;
  dataset_id?: string;
  payload?: Record<string, any>;
};

type PredictionHistory = {
  id: string;
  customer_id: string;
  dataset_id?: string;
  prediction: string;
  probability: number;
  confidence: number;
  created_at: string;
  explanation?: {
    feature: string;
    contribution: number;
  }[];
};

type PredictionResponse = {
  available: boolean;
  reason?: string;
  id?: string;
  prediction?: string;
  probability?: number;
  confidence?: number;
  explanation?: {
    feature: string;
    contribution: number;
  }[];
  model?: {
    features: string[];
  };
};

function PredictionsPage() {
  const [id, setId] = useState("");

  const qc = useQueryClient();

  const customers = useQuery({
    queryKey: ["customers"],
    queryFn: () => platformApi.customers(),
  });

  const history = useQuery({
    queryKey: ["prediction-history"],
    queryFn: platformApi.predictionHistory,
  });

  const predict = useMutation({
    mutationFn: () => platformApi.predict(id),

    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: ["prediction-history"],
      });
    },
  });

  const customerList: Customer[] = customers.data ?? [];

  const historyList: PredictionHistory[] =
    history.data ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Predictions"
        title="Run prediction"
        description="Run machine-learning predictions against customers in your uploaded datasets."
      />

      {/* Prediction form */}
      <Card className="p-6">
        <div className="space-y-5">
          <div>
            <h2 className="text-base font-semibold">
              Customer prediction
            </h2>

            <p className="mt-1 text-sm text-muted-foreground">
              Select a customer and run the trained prediction model.
            </p>
          </div>

          {/* Loading */}
          {customers.isLoading && (
            <div className="rounded-lg border p-4 text-sm text-muted-foreground">
              Loading uploaded customers...
            </div>
          )}

          {/* Error */}
          {customers.isError && (
            <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
              Unable to load customers.
              <br />
              {customers.error instanceof Error
                ? customers.error.message
                : "Unknown error"}
            </div>
          )}

          {/* Empty */}
          {!customers.isLoading &&
            !customers.isError &&
            customerList.length === 0 && (
              <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-4">
                <p className="font-medium">
                  No prediction-ready customers found.
                </p>

                <p className="mt-1 text-sm text-muted-foreground">
                  Upload a customer dataset containing customer records.
                  The dataset should also contain a numeric churn or fraud
                  target for the prediction model.
                </p>
              </div>
            )}

          {/* Customer selector */}
          {customerList.length > 0 && (
            <>
              <div>
                <label className="mb-2 block text-sm font-medium">
                  Select uploaded customer
                </label>

                <select
                  className="
                    w-full rounded-lg border
                    border-border
                    bg-background
                    px-3 py-2.5
                    text-blue-600
                    outline-none
                    transition
                    focus:border-blue-500
                    focus:ring-2
                    focus:ring-blue-500/20
                    dark:text-blue-400
                  "
                  value={id}
                  onChange={(e) => setId(e.target.value)}
                >
                  <option value="" className="text-blue-600">
                    Select customer
                  </option>

                  {customerList.map((customer) => (
                    <option
                      key={customer.id}
                      value={customer.id}
                      className="text-blue-600"
                    >
                      {customer.name || "Unnamed customer"} (
                      {customer.id})
                    </option>
                  ))}
                </select>
              </div>

              <Button
                disabled={!id || predict.isPending}
                onClick={() => predict.mutate()}
              >
                {predict.isPending
                  ? "Running prediction..."
                  : "Run churn prediction"}
              </Button>
            </>
          )}

          {/* Prediction error */}
          {predict.isError && (
            <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
              Prediction failed.
              <br />
              {predict.error instanceof Error
                ? predict.error.message
                : "Unable to run prediction."}
            </div>
          )}

          {/* Prediction result */}
          {predict.data && (
            <PredictionResult result={predict.data} />
          )}
        </div>
      </Card>

      {/* History */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-semibold">
              Prediction history
            </h2>

            <p className="mt-1 text-sm text-muted-foreground">
              Previously generated predictions.
            </p>
          </div>
        </div>

        {history.isLoading && (
          <p className="mt-4 text-sm text-muted-foreground">
            Loading prediction history...
          </p>
        )}

        {!history.isLoading && historyList.length === 0 && (
          <div className="mt-4 rounded-lg border p-5 text-sm text-muted-foreground">
            No predictions have been generated yet.
          </div>
        )}

        {historyList.length > 0 && (
          <div className="mt-5 space-y-3">
            {historyList.map((prediction) => (
              <div
                key={prediction.id}
                className="rounded-lg border p-4"
              >
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-medium">
                      {prediction.customer_id}
                    </p>

                    <p className="text-xs text-muted-foreground">
                      {prediction.created_at}
                    </p>
                  </div>

                  <div className="font-semibold">
                    {prediction.prediction}
                  </div>
                </div>

                <div className="mt-3 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-md bg-muted p-3">
                    <p className="text-xs text-muted-foreground">
                      Probability
                    </p>

                    <p className="mt-1 font-semibold">
                      {(prediction.probability * 100).toFixed(1)}%
                    </p>
                  </div>

                  <div className="rounded-md bg-muted p-3">
                    <p className="text-xs text-muted-foreground">
                      Confidence
                    </p>

                    <p className="mt-1 font-semibold">
                      {(prediction.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>

                {prediction.explanation &&
                  prediction.explanation.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm font-medium">
                        Important features
                      </p>

                      <div className="mt-2 space-y-1">
                        {prediction.explanation.map(
                          (item, index) => (
                            <div
                              key={index}
                              className="flex justify-between text-xs"
                            >
                              <span>
                                {item.feature}
                              </span>

                              <span>
                                {item.contribution > 0
                                  ? "+"
                                  : ""}
                                {item.contribution.toFixed(4)}
                              </span>
                            </div>
                          ),
                        )}
                      </div>
                    </div>
                  )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

function PredictionResult({
  result,
}: {
  result: PredictionResponse;
}) {
  if (result.available === false) {
    return (
      <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-5">
        <p className="font-semibold">
          Prediction unavailable
        </p>

        <p className="mt-1 text-sm text-muted-foreground">
          {result.reason}
        </p>
      </div>
    );
  }

  const probability = result.probability ?? 0;
  const confidence = result.confidence ?? 0;

  const highRisk = result.prediction === "high_churn_risk";

  return (
    <div className="rounded-lg border p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-muted-foreground">
            Prediction
          </p>

          <p className="mt-1 text-xl font-bold">
            {result.prediction}
          </p>
        </div>

        <div className="rounded-full bg-muted px-4 py-2 text-sm font-semibold">
          {highRisk ? "High Risk" : "Low Risk"}
        </div>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg bg-muted p-4">
          <p className="text-xs text-muted-foreground">
            Probability
          </p>

          <p className="mt-1 text-2xl font-bold">
            {(probability * 100).toFixed(1)}%
          </p>
        </div>

        <div className="rounded-lg bg-muted p-4">
          <p className="text-xs text-muted-foreground">
            Confidence
          </p>

          <p className="mt-1 text-2xl font-bold">
            {(confidence * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      {result.explanation &&
        result.explanation.length > 0 && (
          <div className="mt-5">
            <p className="font-medium">
              Top contributing features
            </p>

            <div className="mt-3 space-y-2">
              {result.explanation.map(
                (item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between rounded-md border px-3 py-2"
                  >
                    <span className="text-sm">
                      {item.feature}
                    </span>

                    <span className="text-sm font-medium">
                      {item.contribution > 0
                        ? "+"
                        : ""}
                      {item.contribution.toFixed(4)}
                    </span>
                  </div>
                ),
              )}
            </div>
          </div>
        )}
    </div>
  );
}