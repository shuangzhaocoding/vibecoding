import {
  Button,
  Checkbox,
  DialogBox,
  Form,
  FormItem,
  Grid,
  GridColumn,
  Input,
  Modal,
  Option,
  Pager,
  Select,
} from '@opentiny/vue'
import '@opentiny/vue-theme/index.css'

const components = {
  TinyButton: Button,
  TinyCheckbox: Checkbox,
  TinyDialogBox: DialogBox,
  TinyForm: Form,
  TinyFormItem: FormItem,
  TinyGrid: Grid,
  TinyGridColumn: GridColumn,
  TinyInput: Input,
  TinyOption: Option,
  TinyPager: Pager,
  TinySelect: Select,
}

export function setupTiny(app) {
  Object.entries(components).forEach(([name, comp]) => {
    app.component(name, comp)
  })
  app.config.globalProperties.$Modal = Modal
}

export { Modal }
