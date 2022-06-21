# Sterbefälle 21: Destatis, Sonderauswertung Sterbefälle
# Bevölkerung 20: Destatis
# Impfquoten: Statista

Bundeslaender <- c("Schleswig-Holstein", "Hamburg", "Niedersachsen", "Bremen", "Nordrhein-Westfalen", "Hessen", "Rheinland-Pfalz", "Baden-Wuerttemberg", "Bayern",
"Saarland", "Berlin", "Brandenburg", "Mecklenburg-Vorpommern", "Sachsen", "Sachsen-Anhalt", "Thueringen")



sterbefaelle_21 <- c(36775, 18983, 99792, 8137, 219446, 72030, 50477, 118703, 147237, 14259, 37682, 37337, 24137, 64433, 37142, 34860)
bevoelkerung_20 <- c(2910875, 1852478, 8003421, 680130, 17925570, 6293154, 4098391, 11103043, 13140183, 983991, 3664088, 2531071, 1610774, 4056941, 2180684, 2120237)

sterberaten_21 <- (sterbefaelle_21/bevoelkerung_20) * 100000

impfquoten <- c(80.3, 86.4, 79.6, 90.8, 81.6, 77.6, 78.5, 75.2, 74.9, 83.2, 79.4, 69.6, 75.3, 65.8, 73.8, 70.7)

df_sterb <- data.frame(Bundeslaender, sterberaten_21)
df_impf <- data.frame(Bundeslaender, impfquoten)


df_sterberate <- df_sterb$sterberaten
df_impfquote <- df_impf$impfquoten


plot(df_sterberate, df_impfquote)
text(df_sterberate, df_impfquote, labels=Bundeslaender, cex= 0.7, pos = 2)


modell <- lm(df_impfquote ~ df_sterberate)
abline(modell, col="red")


cor(df_sterb$sterberaten, df_impf$impfquoten, use= "everything", method = "pearson")
