import { useTranslation } from "react-i18next";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GraduationCap, ExternalLink } from "lucide-react";
import { personalInfo } from "@/data/cv-data";

const GitHubIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
  </svg>
);

export function About() {
  const { t } = useTranslation();

  const accounts = [
    {
      handle: "mochapulse",
      url: personalInfo.github,
      role: t("about.accountsMochaRole"),
      desc: t("about.accountsMochaDesc"),
    },
    {
      handle: "dramirezbe",
      url: personalInfo.githubEdu,
      role: t("about.accountsEduRole"),
      desc: t("about.accountsEduDesc"),
    },
  ];

  return (
    <section id="about" className="py-20 bg-background">
      <div className="container mx-auto px-4 md:px-8">
        <h2 className="text-3xl font-bold mb-8 text-primary">
          {t("about.title")}
        </h2>

        <div className="grid gap-8 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-primary">{t("about.profile")}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">
                {t("about.summary")}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="size-5 text-primary" />
                <span className="text-primary">{t("about.education")}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-start justify-between">
                  <h3 className="font-semibold">{t("about.msc")}</h3>
                  <span className="text-sm text-muted-foreground">
                    {t("about.mscPeriod")}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {t("about.institution")}
                </p>
                <p className="text-sm text-muted-foreground">
                  {t("about.mscDetails")}
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex items-start justify-between">
                  <h3 className="font-semibold">{t("about.bsc")}</h3>
                  <span className="text-sm text-muted-foreground">
                    {t("about.bscPeriod")}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {t("about.institution")}
                </p>
                <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                  <li>{t("about.bscDetails1")}</li>
                  <li>{t("about.bscDetails2")}</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GitHubIcon className="size-5 text-primary" />
              <span className="text-primary">{t("about.accountsTitle")}</span>
            </CardTitle>
            <p className="text-sm text-muted-foreground pt-1">
              {t("about.accountsIntro")}
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              {accounts.map((acc) => (
                <a
                  key={acc.handle}
                  href={acc.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group rounded-lg border p-4 transition-colors hover:border-primary hover:bg-muted/50"
                >
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2 font-semibold">
                      <GitHubIcon className="size-4" />@{acc.handle}
                    </span>
                    <ExternalLink className="size-4 text-muted-foreground transition-colors group-hover:text-primary" />
                  </div>
                  <p className="mt-2 text-sm font-medium text-primary">
                    {acc.role}
                  </p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {acc.desc}
                  </p>
                </a>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
