import { useTranslation } from "react-i18next";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Briefcase } from "lucide-react";

export function Experience() {
  const { t } = useTranslation();

  return (
    <section id="experience" className="py-20 bg-muted/30">
      <div className="container mx-auto px-4 md:px-8">
        <h2 className="text-3xl font-bold mb-8 text-primary">
          {t("experience.title")}
        </h2>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Briefcase className="size-5 text-primary" />
                    {t("experience.gcpds")}
                  </CardTitle>
                  <p className="text-muted-foreground mt-1">
                    {t("experience.gcpdsCompany")}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">
                    {t("experience.gcpdsPeriod")}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {t("experience.gcpdsLocation")}
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                <li>{t("experience.gcpdsHighlight1")}</li>
                <li>{t("experience.gcpdsHighlight2")}</li>
                <li>{t("experience.gcpdsHighlight3")}</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Briefcase className="size-5 text-primary" />
                    {t("experience.teaching")}
                  </CardTitle>
                  <p className="text-muted-foreground mt-1">
                    {t("experience.teachingCompany")}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">
                    {t("experience.teachingPeriod")}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {t("experience.teachingLocation")}
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                <li>{t("experience.teachingHighlight1")}</li>
                <li>{t("experience.teachingHighlight2")}</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}
