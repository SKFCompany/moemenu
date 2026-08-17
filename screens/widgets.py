"""
Общие переиспользуемые виджеты для экранов.
"""

from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.label import MDLabel
from kivymd.icon_definitions import md_icons

from data.image_cache import get_cached_path, cache_in_background
from screens.icons import icon_char, category_icon, FALLBACK_ICON, icon_label

# Шрифт иконок Material Design Icons — регистрируется самим KivyMD под
# именем "Icons". Используем его вместо Unicode-эмодзи везде, где текст —
# это ЧИСТО иконка без кириллицы в той же строке (см. подробное
# объяснение в screens/icons.py — почему не обычные emoji).
ICON_FONT = "Icons"


def build_recipe_image(url, category=None, font_style="H2", icon_override=None):
    """
    Возвращает виджет для фото рецепта:

    1. Если картинка уже закэширована на диске — показываем её мгновенно,
       без сети (обычный Image, не AsyncImage).
    2. Если нет — показываем иконку-заглушку сразу и запускаем загрузку
       в фоне (общий пул потоков, см. data/image_cache.py); когда
       картинка скачается — подменяем заглушку на настоящее фото.
       ВАЖНО: раньше здесь ОДНОВРЕМЕННО использовался AsyncImage
       (собственная сетевая загрузка Kivy) И cache_in_background
       (наша собственная загрузка) — то есть каждая некэшированная
       картинка скачивалась ДВАЖДЫ параллельно. При переключении между
       кухнями это давало десятки одновременных загрузок и ощущалось
       как зависание интерфейса. Теперь загрузка ровно одна.
    3. Если картинки нет вовсе, либо загрузка не удалась (нет интернета,
       битая ссылка, 404) — показываем иконку. Если у рецепта есть своя
       валидная иконка Material Design Icons (icon_override — так
       пользователь выбирает "иконку блюда" при добавлении своего
       рецепта в screens/add_recipe.py) — используем её, иначе берём
       иконку по категории рецепта. Старые рецепты, где в этом поле
       исторически хранился обычный Unicode-эмодзи (не имя MDI-иконки),
       просто корректно откатываются на иконку категории.
    """
    if not url:
        return _icon_label(category, font_style, icon_override)

    cached = get_cached_path(url)
    if cached:
        return Image(source=cached, allow_stretch=True, keep_ratio=False)

    placeholder = _icon_label(category, font_style, icon_override)

    def _swap_in_image(local_path):
        # Экран могли пересобрать/уйти с него, пока картинка качалась —
        # заглушка в этом случае уже не часть видимого дерева, менять
        # там нечего (см. подробное объяснение в _replace_with_icon).
        if placeholder.get_root_window() is None:
            return
        parent = placeholder.parent
        if not parent:
            return
        try:
            idx = parent.children.index(placeholder)
        except ValueError:
            idx = 0
        parent.remove_widget(placeholder)
        parent.add_widget(
            Image(source=local_path, allow_stretch=True, keep_ratio=False),
            index=idx,
        )

    cache_in_background(url, on_done=_swap_in_image)
    return placeholder


def _icon_label(category, font_style, icon_override=None):
    if icon_override and icon_override in md_icons:
        text = md_icons[icon_override]
    else:
        text = category_icon(category)
    return icon_label(text, font_style=font_style, halign="center", valign="center")


class TapLabel(ButtonBehavior, MDLabel):
    """Обычный MDLabel, по которому можно тапнуть — для строк в списках,
    которые должны открывать что-то (например, название рецепта в
    результатах "Что можно приготовить?" на экране холодильника)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TapIcon(ButtonBehavior, MDLabel):
    """
    Лёгкая замена MDIconButton для мест, где виджет пересобирается очень
    часто (списки рецептов/покупок/холодильника/меню недели).

    Почему не MDIconButton: он использует внутренние KV-шаблонные
    привязки к общему app.theme_cls, которые не освобождаются
    автоматически при уничтожении виджета — даже explicit
    screens.theme.safe_clear() их не ловит (у kv-правил нет привычного
    __self__, ссылающегося на сам виджет). В экранах, которые
    пересобирают список при каждом обновлении данных, это давало
    реальную и растущую утечку.

    icon — имя иконки Material Design Icons (например "star",
    "close-circle-outline"), НЕ Unicode-эмодзи — см. screens/icons.py,
    почему обычные emoji не подходят на Windows-сборке Kivy.
    """

    def __init__(self, icon, color=None, size_dp=36, **kwargs):
        # font_style нельзя передавать в тот же super().__init__(**kwargs),
        # что и font_name — MDLabel.update_font_style() перезатирает
        # font_name обратно на Roboto при ЛЮБОМ изменении font_style,
        # включая самое первое, во время __init__. Поэтому вынимаем
        # font_style из kwargs, применяем его отдельно, и только ПОСЛЕ
        # этого выставляем font_name — тогда он гарантированно не будет
        # затёрт заново (см. подробности в screens/icons.py::icon_label).
        font_style = kwargs.pop("font_style", "H6")
        super().__init__(**kwargs)
        self.text = icon_char(icon)
        self.font_style = font_style
        self.font_name = ICON_FONT
        self.halign = "center"
        self.valign = "center"
        self.size_hint = (None, None)
        self.size = (dp(size_dp), dp(size_dp))
        if color:
            self.theme_text_color = "Custom"
            self.text_color = color

    def set_icon(self, icon):
        self.text = icon_char(icon)
