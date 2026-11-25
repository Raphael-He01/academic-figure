# Apache-2.0. Workflow integration: Raphael He. All data explicitly simulated.
# In RStudio, source this saved script from the repository root.
# CLI execution is regression testing only; it does not establish GUI inspection.
for (p in c("ggplot2", "patchwork", "jsonlite", "ragg", "svglite", "maps")) {
  if (!requireNamespace(p, quietly = TRUE)) stop("Missing package: ", p)
}
library(ggplot2)
library(patchwork)
source("assets/r-template/R/figure_config.R")
cfg <- figure_config(registry_path = "assets/palettes/catalog.json")
cfg$font_family <- "sans"
cfg$group_levels <- c("Western", "Central", "Eastern")
cfg$group_colors <- stats::setNames(unname(cfg$group_colors), cfg$group_levels)
set.seed(20261116)
n <- 180L
sites <- data.frame(id = sprintf("S%03d", seq_len(n)), longitude = runif(n,-175,175),
                    latitude = runif(n,-55,70), temperature = runif(n,5,35))
sites$group <- factor(ifelse(sites$longitude < -60,"Western",ifelse(sites$longitude < 60,"Central","Eastern")),levels=cfg$group_levels)
sites$response <- 15 + 0.3*sites$temperature + rnorm(n,0,1.8)
sites$split <- ifelse(seq_len(n) <= 120,"train","test")
fit <- lm(response ~ temperature,data=sites,subset=split=="train")
sites$prediction <- as.numeric(predict(fit,newdata=sites));sites$residual <- sites$response-sites$prediction
stamp <- format(Sys.time(),"%Y%m%d-%H%M%S")
out <- file.path("artifacts","demos",stamp)
if (dir.exists(out)) stop("Output exists; wait a second before rerunning")
dir.create(out,recursive=TRUE)
write.csv(sites,file.path(out,"simulated_sites.csv"),row.names=FALSE)
writeLines(capture.output(sessionInfo()),file.path(out,"session.txt"))
theme_set(theme_minimal(base_size=10,base_family="sans") + theme(panel.grid.minor=element_blank(),plot.title=element_text(face="bold"),legend.position="bottom"))
world <- ggplot2::map_data("world")
base <- ggplot()+geom_polygon(data=world,aes(long,lat,group=group),fill="#F0F0EC",colour="#C8CECC",linewidth=.15)+coord_quickmap(xlim=c(-180,180),ylim=c(-60,80),expand=FALSE)+labs(x="Longitude (degrees)",y="Latitude (degrees)")
spatial <- base + geom_point(data=sites,aes(longitude,latitude,colour=group,shape=group),size=1.6,alpha=.85)+scale_colour_manual(values=cfg$group_colors,drop=FALSE)+scale_shape_manual(values=c(16,17,15))+labs(title="Simulated sites | geographic coverage",subtitle="180 generated coordinates; no observed sampling network",colour="Region",shape="Region")
test <- subset(sites,split=="test")
lim <- max(abs(test$residual))
residual_map <- base+geom_point(data=test,aes(longitude,latitude,fill=residual),shape=21,colour="#404749",stroke=.25,size=2)+scale_fill_gradient2(low="#527F94",mid="#FAF8F6",high="#A65F7E",midpoint=0,limits=c(-lim,lim))+labs(title="Held-out residuals | simulation",subtitle="Response minus prediction; 60 held-out sites",fill="Residual (a.u.)")
agreement <- ggplot(test,aes(response,prediction,colour=group,shape=group))+geom_abline(slope=1,intercept=0,linetype=2,colour="#69727B")+geom_point(size=2)+scale_colour_manual(values=cfg$group_colors,drop=FALSE)+scale_shape_manual(values=c(16,17,15))+coord_equal()+labs(title="a  Held-out agreement",x="Observed response (a.u.)",y="Predicted response (a.u.)",colour="Region",shape="Region")
errors <- ggplot(test,aes(prediction,residual,colour=group,shape=group))+geom_hline(yintercept=0,linetype=2,colour="#69727B")+geom_point(size=2)+scale_colour_manual(values=cfg$group_colors,drop=FALSE)+scale_shape_manual(values=c(16,17,15))+labs(title="b  Residual structure",x="Predicted response (a.u.)",y="Residual (a.u.)",colour="Region",shape="Region")
model_plot <- agreement+errors+plot_layout(guides="collect")+plot_annotation(title="Prediction diagnostics | simulated linear response",subtitle="120 training / 60 test records; training-only fit; fixed seed")
plots <- list(global_sites=spatial,spatial_residuals=residual_map,model_diagnostics=model_plot)
manifest <- list()
for (name in names(plots)) {
  fig <- plots[[name]]; width <- if(name=="model_diagnostics") 183 else 160; height <- if(name=="model_diagnostics") 100 else 105
  ggsave(file.path(out,paste0(name,".svg")),fig,device=svglite::svglite,width=width,height=height,units="mm",bg="white")
  ggsave(file.path(out,paste0(name,".png")),fig,device=ragg::agg_png,width=width,height=height,units="mm",dpi=300,bg="white")
  if (identical(Sys.info()[["sysname"]],"Darwin") && capabilities("aqua")) {
    device <- function(filename,width,height,...) grDevices::quartz(file=filename,type="pdf",width=width,height=height,...);devname <- "quartz"
  } else if (capabilities("cairo")) {
    device <- grDevices::cairo_pdf;devname <- "cairo_pdf"
  } else {device <- grDevices::pdf;devname <- "base_pdf_unverified_fonts"}
  ggsave(file.path(out,paste0(name,".pdf")),fig,device=device,width=width,height=height,units="mm",bg="white")
  manifest[[name]] <- list(stem=name,width_mm=width,height_mm=height,png_dpi=300,pdf_device=devname,palette_id=cfg$palette$id,palette_version=cfg$palette$version,group_mapping=as.list(cfg$group_colors),acceptance="pending",simulation=TRUE)
}
jsonlite::write_json(manifest,file.path(out,"export_manifest.json"),pretty=TRUE,auto_unbox=TRUE)
rmse <- sqrt(mean(test$residual^2)); mae <- mean(abs(test$residual))
caption <- c("作者/工作流整合：Raphael He。全部为固定种子的模拟数据，不代表真实科研发现。",
"图1：模拟站点的全球位置。180个随机坐标；颜色和点形代表由经度定义的三个演示分组。底图来自已安装的 maps 包，仅提供空间背景；本图不代表真实覆盖或抽样设计。",
"图2：60个留出站点的残差。残差为模拟响应减训练模型预测，色标以零为中心；保留全部留出记录。地理位置未参与生成响应，不能解释为空间因果效应。",
"图3：留出预测及残差诊断。120条训练记录拟合响应对温度的线性模型；60条留出记录用于诊断。虚线为恒等线或零残差。未绘制置信或预测区间，也未执行显著性检验。",
sprintf("Results演示：该模拟留出集的 RMSE 为 %.3f a.u.，MAE 为 %.3f a.u.；仅说明本次生成数据与拟合过程，不构成外部验证。",rmse,mae))
writeLines(caption,file.path(out,"caption-and-results-zh.txt"),useBytes=TRUE)
if (interactive()) print(model_plot)
cat("Draft simulation demos written to ",out,"; final-size visual/scientific QA pending.\n",sep="")
