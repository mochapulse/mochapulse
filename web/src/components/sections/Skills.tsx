import { useTranslation } from "react-i18next";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Code, Globe, Server } from "lucide-react";
import {
  CIcon,
  CplusplusIcon,
  PythonIcon,
  JavascriptIcon,
  TypescriptIcon,
  MysqlIcon,
  ReactIcon,
  ViteIcon,
  NodejsIcon,
  DockerIcon,
  LinuxIcon,
  GitIcon,
  RaspberrypiIcon,
  FastapiIcon,
  DjangoIcon,
} from "devicon-kit";

const skillCategories = [
  {
    key: "languages",
    icon: <Code className="size-5 text-primary" />,
    items: [
      { name: "C99", icon: <CIcon className="size-5" /> },
      { name: "C++", icon: <CplusplusIcon className="size-5" /> },
      { name: "Python", icon: <PythonIcon className="size-5" /> },
      { name: "JavaScript", icon: <JavascriptIcon className="size-5" /> },
      { name: "TypeScript", icon: <TypescriptIcon className="size-5" /> },
      { name: "SQL", icon: <MysqlIcon className="size-5" /> },
    ],
  },
  {
    key: "frameworks",
    icon: <Globe className="size-5 text-primary" />,
    items: [
      { name: "FastAPI", icon: <FastapiIcon className="size-5" /> },
      { name: "Django", icon: <DjangoIcon className="size-5" /> },
      { name: "React", icon: <ReactIcon className="size-5" /> },
      { name: "Vite", icon: <ViteIcon className="size-5" /> },
      { name: "Node.js", icon: <NodejsIcon className="size-5" /> },
    ],
  },
  {
    key: "infrastructure",
    icon: <Server className="size-5 text-primary" />,
    items: [
      { name: "Linux", icon: <LinuxIcon className="size-5" /> },
      { name: "Docker", icon: <DockerIcon className="size-5" /> },
      { name: "Git", icon: <GitIcon className="size-5" /> },
      { name: "Raspberry Pi", icon: <RaspberrypiIcon className="size-5" /> },
    ],
  },
];

export function Skills() {
  const { t } = useTranslation();

  return (
    <section id="skills" className="py-20 bg-muted/30">
      <div className="container mx-auto px-4 md:px-8">
        <h2 className="text-3xl font-bold mb-8 text-primary">
          {t("skills.title")}
        </h2>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {skillCategories.map((category, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {category.icon}
                  <span>{t(`skills.${category.key}`)}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-3">
                  {category.items.map((item, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {item.icon}
                      <span>{item.name}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>{t("skills.spokenLanguages")}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center gap-2">
                <Badge variant="secondary">Spanish</Badge>
                <span className="text-sm text-muted-foreground">Native</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary">English</Badge>
                <span className="text-sm text-muted-foreground">
                  Intermediate (B1)
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
